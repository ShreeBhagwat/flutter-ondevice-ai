import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';

import '../models/history_entry.dart';
import '../models/model_config.dart';
import '../models/prediction.dart';
import '../services/classifier.dart';
import '../services/history_store.dart';
import 'history_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _picker = ImagePicker();
  final _history = HistoryStore();

  ModelConfig _model = ModelConfig.efficientNet;
  Classifier? _classifier;
  bool _ready = false; // model + history loaded
  bool _busy = false; // picking or analysing

  // What is currently shown on screen.
  File? _image;
  List<Prediction> _results = [];
  int? _timeMs;
  String? _resultModel;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    await _history.load();
    await _loadModel(_model);
  }

  Future<void> _loadModel(ModelConfig model) async {
    setState(() => _ready = false);
    _classifier?.dispose();
    final classifier = Classifier(model);
    await classifier.load();
    if (!mounted) return classifier.dispose();
    setState(() {
      _model = model;
      _classifier = classifier;
      _ready = true;
    });
  }

  @override
  void dispose() {
    _classifier?.dispose();
    super.dispose();
  }

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------

  Future<void> _pickImage(ImageSource source) async {
    // Ignore extra taps while the camera/gallery is already opening,
    // otherwise image_picker throws PlatformException(multiple_request).
    if (_busy) return;
    setState(() => _busy = true);

    XFile? picked;
    try {
      picked = await _picker.pickImage(source: source, maxWidth: 1024);
    } on PlatformException catch (e) {
      // e.g. camera permission denied, or no camera (simulator).
      _showMessage('Could not open ${source.name}: ${e.message}');
    }

    if (picked == null) {
      setState(() => _busy = false); // user cancelled or error
      return;
    }
    await _analyse(File(picked.path));
  }

  /// Runs the AI on [image], shows the result and saves it to history.
  Future<void> _analyse(File image) async {
    setState(() {
      _busy = true;
      _image = image;
      _results = [];
      _timeMs = null;
    });

    try {
      final stopwatch = Stopwatch()..start();
      final results = await _classifier!.classify(image);
      stopwatch.stop();

      final entry = await _history.add(
        image: image,
        predictions: results,
        inferenceMs: stopwatch.elapsedMilliseconds,
        modelName: _model.name,
      );

      if (!mounted) return;
      setState(() {
        // Point at the saved copy, so Retry works even if the camera's
        // temporary file is cleaned up by the OS.
        _image = _history.imageFor(entry);
        _results = results;
        _timeMs = entry.inferenceMs;
        _resultModel = entry.modelName;
      });
    } catch (e) {
      _showMessage('Could not analyse this image: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  /// Run the current photo through the (possibly different) model again.
  void _retry() {
    if (_image != null && !_busy) _analyse(_image!);
  }

  void _clear() {
    setState(() {
      _image = null;
      _results = [];
      _timeMs = null;
      _resultModel = null;
    });
  }

  Future<void> _openHistory() async {
    final entry = await Navigator.push<HistoryEntry>(
      context,
      MaterialPageRoute(builder: (_) => HistoryScreen(store: _history)),
    );
    if (entry == null) {
      // The shown photo may have been deleted from history.
      if (_image != null && !await _image!.exists()) _clear();
      return;
    }
    setState(() {
      _image = _history.imageFor(entry);
      _results = entry.predictions;
      _timeMs = entry.inferenceMs;
      _resultModel = entry.modelName;
    });
  }

  void _showMessage(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
  }

  // ---------------------------------------------------------------------------
  // UI
  // ---------------------------------------------------------------------------

  @override
  Widget build(BuildContext context) {
    final canAct = _ready && !_busy;
    return Scaffold(
      appBar: AppBar(
        title: const Text('What is this?'),
        actions: [
          _buildModelMenu(canAct),
          IconButton(
            tooltip: 'History',
            icon: const Icon(Icons.history),
            onPressed: canAct ? _openHistory : null,
          ),
          IconButton(
            tooltip: 'Clear',
            icon: const Icon(Icons.clear),
            onPressed: canAct && _image != null ? _clear : null,
          ),
        ],
      ),
      body: !_ready
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 12),
                  Text('Loading ${_model.name}…'),
                ],
              ),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildImagePreview(),
                const SizedBox(height: 16),
                if (_busy && _image != null)
                  const Center(child: CircularProgressIndicator()),
                if (_results.isNotEmpty && !_busy) ..._buildResults(),
              ],
            ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: canAct ? () => _pickImage(ImageSource.camera) : null,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Camera'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: canAct ? () => _pickImage(ImageSource.gallery) : null,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Gallery'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildModelMenu(bool enabled) {
    return PopupMenuButton<ModelConfig>(
      tooltip: 'Choose AI model',
      icon: const Icon(Icons.memory),
      enabled: enabled,
      initialValue: _model,
      onSelected: (m) {
        if (m != _model) _loadModel(m);
      },
      itemBuilder: (_) => [
        for (final m in ModelConfig.all)
          CheckedPopupMenuItem(
            value: m,
            checked: m == _model,
            child: ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(m.name),
              subtitle: Text(m.description),
            ),
          ),
      ],
    );
  }

  Widget _buildImagePreview() {
    return AspectRatio(
      aspectRatio: 1,
      child: Container(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16),
        ),
        clipBehavior: Clip.antiAlias,
        child: _image == null
            ? Center(
                child: Text(
                  'Take or pick a photo to start\nModel: ${_model.name}',
                  textAlign: TextAlign.center,
                ),
              )
            : Image.file(_image!, fit: BoxFit.cover),
      ),
    );
  }

  List<Widget> _buildResults() {
    final top = _results.first;
    final textTheme = Theme.of(context).textTheme;
    return [
      if (top.confidence < 0.3)
        Card(
          color: Theme.of(context).colorScheme.tertiaryContainer,
          child: const ListTile(
            leading: Icon(Icons.help_outline),
            title: Text('Not very sure'),
            subtitle: Text('Try a closer, well-lit photo of one object, '
                'or switch model and Retry.'),
          ),
        ),
      ..._results.map(_buildResultTile),
      const SizedBox(height: 8),
      Text(
        'By $_resultModel on your phone in $_timeMs ms — no internet used.',
        textAlign: TextAlign.center,
        style: textTheme.bodySmall,
      ),
      const SizedBox(height: 8),
      Center(
        child: OutlinedButton.icon(
          onPressed: _ready && !_busy ? _retry : null,
          icon: const Icon(Icons.refresh),
          label: Text('Retry with ${_model.name}'),
        ),
      ),
    ];
  }

  Widget _buildResultTile(Prediction p) {
    return Card(
      child: ListTile(
        title: Text(p.label),
        subtitle: LinearProgressIndicator(value: p.confidence),
        trailing: Text(p.percent),
      ),
    );
  }
}
