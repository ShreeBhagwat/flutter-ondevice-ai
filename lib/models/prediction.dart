/// One guess from the AI model, e.g. "golden retriever" with 0.87 confidence.
class Prediction {
  final String label;

  /// A number from 0.0 to 1.0 — how sure the model is.
  final double confidence;

  const Prediction(this.label, this.confidence);

  /// Confidence as a friendly percentage string, e.g. "87.3%".
  String get percent => '${(confidence * 100).toStringAsFixed(1)}%';

  Map<String, dynamic> toJson() => {'label': label, 'confidence': confidence};

  factory Prediction.fromJson(Map<String, dynamic> json) => Prediction(
    json['label'] as String,
    (json['confidence'] as num).toDouble(),
  );
}
