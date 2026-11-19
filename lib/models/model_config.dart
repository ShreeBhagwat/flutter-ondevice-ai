/// Describes one AI model file the app can use.
///
/// To try a new model (e.g. one you trained with Teachable Machine):
///   1. put the .tflite + labels file in assets/models/
///   2. list them in pubspec.yaml
///   3. add a new ModelConfig below and to [all]
class ModelConfig {
  final String name;
  final String description;
  final String modelPath;
  final String labelsPath;

  const ModelConfig({
    required this.name,
    required this.description,
    required this.modelPath,
    required this.labelsPath,
  });

  /// Default: more accurate. ~81% top-1 accuracy on ImageNet, 300x300 input.
  static const efficientNet = ModelConfig(
    name: 'EfficientNet-Lite4',
    description: 'Accurate · 15 MB · 300×300',
    modelPath: 'assets/models/efficientnet_lite4.tflite',
    labelsPath: 'assets/models/labels_1000.txt',
  );

  /// Smaller and faster, but less accurate. ~70% top-1, 224x224 input.
  static const mobileNet = ModelConfig(
    name: 'MobileNet V1',
    description: 'Fast · 4 MB · 224×224',
    modelPath: 'assets/models/mobilenet.tflite',
    labelsPath: 'assets/models/mobilenet_labels.txt',
  );

  static const all = [efficientNet, mobileNet];

  static ModelConfig byName(String name) =>
      all.firstWhere((m) => m.name == name, orElse: () => efficientNet);
}
