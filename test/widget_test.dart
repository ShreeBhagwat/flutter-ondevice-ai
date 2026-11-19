import 'package:flutter_test/flutter_test.dart';
import 'package:ondevice_ai/models/history_entry.dart';
import 'package:ondevice_ai/models/prediction.dart';

void main() {
  test('Prediction formats confidence as a percentage', () {
    expect(const Prediction('cat', 0.873).percent, '87.3%');
  });

  test('HistoryEntry survives a JSON round trip', () {
    final e = HistoryEntry(
      id: '1',
      imageFileName: '1.jpg',
      predictions: const [Prediction('daisy', 0.91), Prediction('vase', 0.01)],
      createdAt: DateTime(2026, 11, 19, 12, 30),
      inferenceMs: 120,
      modelName: 'EfficientNet-Lite4',
    );
    final back = HistoryEntry.fromJson(e.toJson());
    expect(back.top!.label, 'daisy');
    expect(back.predictions.length, 2);
    expect(back.createdAt, e.createdAt);
    expect(back.modelName, 'EfficientNet-Lite4');
  });
}
