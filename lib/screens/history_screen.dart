import 'package:flutter/material.dart';

import '../models/history_entry.dart';
import '../services/history_store.dart';

/// Shows every past result. Tap one to open it on the home screen
/// (where you can Retry it); swipe left to delete.
class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key, required this.store});

  final HistoryStore store;

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  Future<void> _confirmClearAll() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear all history?'),
        content: const Text('This deletes every saved photo and result.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Clear all'),
          ),
        ],
      ),
    );
    if (ok == true) {
      await widget.store.clear();
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    final entries = widget.store.entries;
    return Scaffold(
      appBar: AppBar(
        title: Text('History (${entries.length})'),
        actions: [
          IconButton(
            tooltip: 'Clear all',
            icon: const Icon(Icons.delete_sweep),
            onPressed: entries.isEmpty ? null : _confirmClearAll,
          ),
        ],
      ),
      body: entries.isEmpty
          ? const Center(child: Text('No photos analysed yet'))
          : ListView.separated(
              itemCount: entries.length,
              separatorBuilder: (_, _) => const Divider(height: 1),
              itemBuilder: (context, i) => _buildTile(entries[i]),
            ),
    );
  }

  Widget _buildTile(HistoryEntry e) {
    final top = e.top;
    return Dismissible(
      key: ValueKey(e.id),
      direction: DismissDirection.endToStart,
      background: Container(
        color: Colors.red,
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      onDismissed: (_) async {
        await widget.store.delete(e);
        setState(() {});
      },
      child: ListTile(
        leading: ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Image.file(
            widget.store.imageFor(e),
            width: 56,
            height: 56,
            fit: BoxFit.cover,
            cacheWidth: 168,
            errorBuilder: (_, _, _) => const SizedBox(
              width: 56,
              height: 56,
              child: Icon(Icons.broken_image),
            ),
          ),
        ),
        title: Text(top?.label ?? '—'),
        subtitle: Text(
          '${top?.percent ?? ''} · ${e.modelName}\n'
          '${_formatDate(e.createdAt)} · ${e.inferenceMs} ms',
        ),
        isThreeLine: true,
        trailing: const Icon(Icons.chevron_right),
        onTap: () => Navigator.pop(context, e),
      ),
    );
  }

  static String _formatDate(DateTime d) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    String two(int n) => n.toString().padLeft(2, '0');
    return '${d.day} ${months[d.month - 1]} ${two(d.hour)}:${two(d.minute)}';
  }
}
