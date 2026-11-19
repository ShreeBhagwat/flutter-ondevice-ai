import 'dart:io';
import 'dart:isolate';
import 'dart:typed_data';

import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

import '../models/model_config.dart';
import '../models/prediction.dart';

/// The "brain" of the app. Everything AI-related lives in this one file.
///
/// On-device image classification is always the same 4 steps:
///
///   1. LOAD        the model file (.tflite) and its labels (.txt)
///   2. PREPROCESS  the photo into the exact shape the model expects
///   3. RUN         the model (inference) – this happens on the phone, no internet
///   4. POSTPROCESS the raw numbers into human-readable answers
///
/// This classifier reads the input size, data type and quantization straight
/// from the model file, so the same code works for EfficientNet, MobileNet,
/// or a model you trained yourself.
class Classifier {
  Classifier(this.config);

  final ModelConfig config;

  late final Interpreter _interpreter;
  late final List<String> _labels;
  late final int
  _inputSize; // e.g. 300 for EfficientNet-Lite4, 224 for MobileNet

  // ---------------------------------------------------------------------------
  // STEP 1: LOAD
  // ---------------------------------------------------------------------------
  Future<void> load() async {
    _interpreter = await Interpreter.fromAsset(config.modelPath);

    final labelsText = await rootBundle.loadString(config.labelsPath);
    _labels = labelsText
        .split('\n')
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        // Teachable Machine writes "0 Apple", "1 Banana"… — drop the number.
        .map((line) => line.replaceFirst(RegExp(r'^\d+\s+'), ''))
        .toList();

    // Ask the model what it expects. Shape is [1, height, width, 3].
    final input = _interpreter.getInputTensor(0);
    final output = _interpreter.getOutputTensor(0);
    _inputSize = input.shape[1];

    // Handy for class: see exactly what the model wants and returns.
    // ignore: avoid_print
    print(
      '[${config.name}] input : ${input.shape} ${input.type} ${input.params}',
    );
    // ignore: avoid_print
    print(
      '[${config.name}] output: ${output.shape} ${output.type} ${output.params}',
    );
  }

  /// Takes a photo file and returns the model's top [topK] guesses.
  Future<List<Prediction>> classify(File imageFile, {int topK = 3}) async {
    final bytes = await imageFile.readAsBytes();
    final pixels = await _preprocessInBackground(bytes, _inputSize);
    final scores = _runModel(pixels);
    return _postprocess(scores, topK);
  }

  /// Decoding/resizing a big photo is slow, so do it on a background
  /// isolate (thread) to keep the UI smooth. (Static, so the closure
  /// doesn't capture the interpreter, which can't move between isolates.)
  static Future<Uint8List> _preprocessInBackground(Uint8List bytes, int size) =>
      Isolate.run(() => _preprocess(bytes, size));

  // ---------------------------------------------------------------------------
  // STEP 2: PREPROCESS
  // ---------------------------------------------------------------------------
  /// Photo bytes → square [size x size] image → flat list of R,G,B bytes.
  static Uint8List _preprocess(Uint8List bytes, int size) {
    // Decode JPEG/PNG into pixels, and fix rotation from the camera.
    final decoded = img.bakeOrientation(img.decodeImage(bytes)!);

    // Centre-crop to a square first, so the object isn't squashed.
    // (Models were trained on undistorted images → better accuracy.)
    final side = decoded.width < decoded.height
        ? decoded.width
        : decoded.height;
    final cropped = img.copyCrop(
      decoded,
      x: (decoded.width - side) ~/ 2,
      y: (decoded.height - side) ~/ 2,
      width: side,
      height: side,
    );

    // Resize to exactly what the model was trained on.
    final resized = img.copyResize(
      cropped,
      width: size,
      height: size,
      interpolation: img.Interpolation.average,
    );

    // size*size pixels × 3 colours, each 0..255, in R,G,B order.
    return resized.getBytes(order: img.ChannelOrder.rgb);
  }

  // ---------------------------------------------------------------------------
  // STEP 3: RUN (inference)
  // ---------------------------------------------------------------------------
  /// Feeds the pixels through the neural network. Runs fully on-device.
  List<double> _runModel(Uint8List rgb) {
    final input = _interpreter.getInputTensor(0);
    final output = _interpreter.getOutputTensor(0);

    if (input.type == TensorType.uint8) {
      // Quantized model: takes raw 0..255 pixel bytes directly.
      input.data = rgb;
    } else {
      // Float model: one 32-bit number per colour value (0.0..255.0).
      input.data = Float32List.fromList(rgb.map((v) => v.toDouble()).toList())
          .buffer
          .asUint8List();
    }

    _interpreter.invoke(); // <- the actual AI happens here

    // Read the raw answer: one score per label.
    final raw = Uint8List.fromList(output.data);
    if (output.type == TensorType.uint8) {
      // De-quantize: real value = (byte - zeroPoint) * scale
      final q = output.params;
      return [for (final b in raw) (b - q.zeroPoint) * q.scale];
    }
    return raw.buffer.asFloat32List().toList();
  }

  // ---------------------------------------------------------------------------
  // STEP 4: POSTPROCESS
  // ---------------------------------------------------------------------------
  /// Raw scores → top-K labels with a confidence between 0 and 1.
  List<Prediction> _postprocess(List<double> scores, int topK) {
    final predictions = <Prediction>[
      for (var i = 0; i < scores.length && i < _labels.length; i++)
        Prediction(_labels[i], scores[i].clamp(0.0, 1.0)),
    ];
    predictions.sort((a, b) => b.confidence.compareTo(a.confidence));
    return predictions.take(topK).toList();
  }

  void dispose() => _interpreter.close();
}
