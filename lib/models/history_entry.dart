import 'prediction.dart';

/// One past classification: which photo, what the AI said, and when.
class HistoryEntry {
  final String id;

  /// File name only (inside the app's history folder). We don't store the
  /// full path because iOS changes the app folder path on every reinstall.
  final String imageFileName;
  final List<Prediction> predictions;
  final DateTime createdAt;
  final int inferenceMs;
  final String modelName;

  const HistoryEntry({
    required this.id,
    required this.imageFileName,
    required this.predictions,
    required this.createdAt,
    required this.inferenceMs,
    required this.modelName,
  });

  Prediction? get top => predictions.isEmpty ? null : predictions.first;

  Map<String, dynamic> toJson() => {
    'id': id,
    'image': imageFileName,
    'predictions': predictions.map((p) => p.toJson()).toList(),
    'createdAt': createdAt.toIso8601String(),
    'ms': inferenceMs,
    'model': modelName,
  };

  factory HistoryEntry.fromJson(Map<String, dynamic> json) => HistoryEntry(
    id: json['id'] as String,
    imageFileName: json['image'] as String,
    predictions: (json['predictions'] as List)
        .map((p) => Prediction.fromJson(p as Map<String, dynamic>))
        .toList(),
    createdAt: DateTime.parse(json['createdAt'] as String),
    inferenceMs: json['ms'] as int,
    modelName: json['model'] as String,
  );
}
