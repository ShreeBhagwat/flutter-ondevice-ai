import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

import '../models/history_entry.dart';
import '../models/prediction.dart';

/// Saves past results on the phone so they survive app restarts.
///
/// Layout inside the app's private Documents folder:
///   `history/history.json`  ← list of entries (newest first)
///   `history/ID.jpg`        ← a copy of each photo
class HistoryStore {
  late final Directory _dir;
  late final File _indexFile;
  final List<HistoryEntry> _entries = [];

  /// Newest first.
  List<HistoryEntry> get entries => List.unmodifiable(_entries);

  Future<void> load() async {
    final docs = await getApplicationDocumentsDirectory();
    _dir = Directory('${docs.path}/history');
    await _dir.create(recursive: true);
    _indexFile = File('${_dir.path}/history.json');

    if (await _indexFile.exists()) {
      try {
        final list = jsonDecode(await _indexFile.readAsString()) as List;
        _entries
          ..clear()
          ..addAll(list.map((e) => HistoryEntry.fromJson(e as Map<String, dynamic>)));
      } catch (_) {
        // Corrupt file: start with an empty history rather than crash.
        _entries.clear();
      }
    }
  }

  File imageFor(HistoryEntry e) => File('${_dir.path}/${e.imageFileName}');

  /// Copies the photo into the history folder and records the result.
  Future<HistoryEntry> add({
    required File image,
    required List<Prediction> predictions,
    required int inferenceMs,
    required String modelName,
  }) async {
    final id = DateTime.now().microsecondsSinceEpoch.toString();
    final fileName = '$id.jpg';
    // Each entry keeps its own copy, so deleting one never breaks another.
    await image.copy('${_dir.path}/$fileName');

    final entry = HistoryEntry(
      id: id,
      imageFileName: fileName,
      predictions: predictions,
      createdAt: DateTime.now(),
      inferenceMs: inferenceMs,
      modelName: modelName,
    );
    _entries.insert(0, entry);
    await _save();
    return entry;
  }

  Future<void> delete(HistoryEntry entry) async {
    _entries.removeWhere((e) => e.id == entry.id);
    final file = imageFor(entry);
    if (await file.exists()) await file.delete();
    await _save();
  }

  Future<void> clear() async {
    for (final e in List.of(_entries)) {
      final file = imageFor(e);
      if (await file.exists()) await file.delete();
    }
    _entries.clear();
    await _save();
  }

  Future<void> _save() => _indexFile
      .writeAsString(jsonEncode(_entries.map((e) => e.toJson()).toList()));
}
