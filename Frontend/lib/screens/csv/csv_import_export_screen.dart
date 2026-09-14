import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:intl/intl.dart';
import '../../services/csv_service.dart';
import '../../providers/transaction_provider.dart';
import '../../providers/report_provider.dart';

class CsvImportExportScreen extends ConsumerStatefulWidget {
  const CsvImportExportScreen({super.key});

  @override
  ConsumerState<CsvImportExportScreen> createState() => _CsvImportExportScreenState();
}

class _CsvImportExportScreenState extends ConsumerState<CsvImportExportScreen>
    with SingleTickerProviderStateMixin {
  final _csvService = CsvService();
  bool _importing = false;
  bool _exporting = false;
  bool _analyzing = false;
  bool _showGuidelines = false;
  String? _result;
  Map<String, dynamic>? _analysis;
  String? _pickedFilePath;
  String? _pickedFileName;

  late final AnimationController _guidelinesAnim;

  @override
  void initState() {
    super.initState();
    _guidelinesAnim = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
  }

  @override
  void dispose() {
    _guidelinesAnim.dispose();
    super.dispose();
  }

  Future<void> _pickAndAnalyzeFile() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['csv'],
    );
    if (result.isEmpty) return;
    final filePath = result.first.path;
    if (filePath == null) return;

    setState(() {
      _pickedFilePath = filePath;
      _pickedFileName = result.first.name;
      _analysis = null;
      _result = null;
      _analyzing = true;
    });

    try {
      final analysis = await _csvService.analyzeCsv(filePath);
      setState(() => _analysis = analysis);
    } catch (e) {
      setState(() => _result = 'Analysis failed: $e');
    } finally {
      setState(() => _analyzing = false);
    }
  }

  Future<void> _confirmImport() async {
    if (_pickedFilePath == null) return;

    // Show confirmation dialog
    final validCount = _analysis?['valid_rows'] ?? 0;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Confirm Import'),
        content: Text('Import $validCount valid transactions?\n\n'
            'Invalid rows will be skipped (see errors below).'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Import'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;

    setState(() {
      _importing = true;
      _result = null;
    });

    try {
      final res = await _csvService.importCsv(_pickedFilePath!);
      final imported = res['imported'];
      final failed = res['failed'] as List?;
      final total = res['total_rows'] ?? '?';
      setState(() {
        _result = 'Import complete!\n\n'
            'Total rows: $total\n'
            'Imported: $imported\n'
            'Failed: ${failed?.length ?? 0}';
        if (failed != null && failed.isNotEmpty) {
          _result =
              '$_result\n\nFailed rows:\n${failed.map((f) => 'Row ${f['row']}: ${f['reason']}').join('\n')}';
        }
        // Clear the picked file after import
        _analysis = null;
        _pickedFilePath = null;
        _pickedFileName = null;
      });
      // Refresh transaction list and reports so imported data shows up
      if (imported > 0) {
        ref.read(transactionProvider.notifier).loadTransactions();
        ref.invalidate(reportProvider);
      }
    } catch (e) {
      setState(() => _result = 'Import error: $e');
    } finally {
      setState(() => _importing = false);
    }
  }

  Future<void> _exportCsv() async {
    setState(() {
      _exporting = true;
      _result = null;
      _analysis = null;
    });

    try {
      final csvContent = await _csvService.exportCsv();
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final fileName = 'expense_mate_$timestamp.csv';

      final csvBytes = Uint8List.fromList(utf8.encode(csvContent));

      final savedUri = await FilePicker.saveFile(
        dialogTitle: 'Save CSV Export',
        fileName: fileName,
        bytes: csvBytes,
        type: FileType.custom,
        allowedExtensions: ['csv'],
      );

      if (savedUri == null) {
        setState(() => _result = 'Export cancelled.');
        return;
      }

      final file = File.fromUri(savedUri);
      await file.writeAsBytes(csvBytes);

      setState(() {
        _result = 'Exported successfully!\n\nSaved to:\n${savedUri.path}\n\n'
            'You can find this file in your file manager and re-import it later.';
      });
    } catch (e) {
      setState(() => _result = 'Export error: $e');
    } finally {
      setState(() => _exporting = false);
    }
  }

  void _toggleGuidelines() {
    setState(() => _showGuidelines = !_showGuidelines);
    if (_showGuidelines) {
      _guidelinesAnim.forward();
    } else {
      _guidelinesAnim.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('CSV Import / Export')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // --- Guidelines Section ---
          _buildGuidelinesSection(theme),
          const SizedBox(height: 16),

          // --- Action Buttons ---
          OutlinedButton.icon(
            onPressed: _importing || _analyzing ? null : _pickAndAnalyzeFile,
            icon: const Icon(Icons.upload_file),
            label: const Text('Pick & Analyze CSV'),
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _exporting ? null : _exportCsv,
            icon: const Icon(Icons.download),
            label: _exporting
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Export All Transactions'),
          ),
          const SizedBox(height: 16),

          // --- Analysis Results ---
          if (_analyzing)
            const Padding(
              padding: EdgeInsets.all(24),
              child: Center(child: CircularProgressIndicator()),
            ),
          if (_analysis != null) _buildAnalysisCard(theme),
          if (_result != null) _buildResultCard(theme),
        ],
      ),
    );
  }

  Widget _buildGuidelinesSection(ThemeData theme) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('CSV Format Guidelines'),
            trailing: Icon(
              _showGuidelines
                  ? Icons.keyboard_arrow_up
                  : Icons.keyboard_arrow_down,
            ),
            onTap: _toggleGuidelines,
          ),
          SizeTransition(
            sizeFactor: _guidelinesAnim,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Required columns:',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                  const SizedBox(height: 8),
                  _guidelineRow('type', "Required. 'income' or 'expense'",
                      Icons.check_circle, Colors.green),
                  _guidelineRow('amount', 'Required. Positive number (e.g. 1500)',
                      Icons.check_circle, Colors.green),
                  _guidelineRow('date', 'Required. Format: YYYY-MM-DD',
                      Icons.check_circle, Colors.green),
                  _guidelineRow('category', 'Category name (e.g. Food, Transport)',
                      Icons.circle_outlined, Colors.grey),
                  _guidelineRow('category_id', 'Category ID number (alternative to name)',
                      Icons.circle_outlined, Colors.grey),
                  _guidelineRow('currency', 'Currency code (defaults to PKR)',
                      Icons.circle_outlined, Colors.grey),
                  _guidelineRow('description', 'Any text (optional)',
                      Icons.circle_outlined, Colors.grey),
                  const Divider(height: 20),
                  const Text(
                    'Example row:',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      'expense,Food,3,1500,PKR,2025-01-15,Lunch at cafe',
                      style: TextStyle(fontSize: 12, fontFamily: 'monospace'),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Tip: Export your data first to get a template with your categories.',
                    style: TextStyle(
                      fontSize: 12,
                      color: theme.colorScheme.primary,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _guidelineRow(
      String col, String desc, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 6),
          Text(
            col,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              fontFamily: 'monospace',
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(desc, style: const TextStyle(fontSize: 12)),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisCard(ThemeData theme) {
    final a = _analysis!;
    final totalRows = a['total_rows'] ?? 0;
    final validRows = a['valid_rows'] ?? 0;
    final invalidRows = a['invalid_rows'] ?? 0;
    final columnsFound = (a['columns_found'] as List?)?.cast<String>() ?? [];
    final columnsMissing = (a['columns_missing'] as List?)?.cast<String>() ?? [];
    final preview = (a['preview'] as List?) ?? [];
    final errors = (a['errors'] as List?) ?? [];
    final categories = (a['categories_available'] as List?) ?? [];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // File info
            Row(
              children: [
                Icon(Icons.description, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _pickedFileName ?? 'Unknown file',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Row summary
            Row(
              children: [
                _statChip('Total', '$totalRows', Colors.blue),
                const SizedBox(width: 8),
                _statChip('Valid', '$validRows', Colors.green),
                const SizedBox(width: 8),
                _statChip('Invalid', '$invalidRows',
                    invalidRows > 0 ? Colors.red : Colors.grey),
              ],
            ),
            const SizedBox(height: 12),

            // Columns check
            if (columnsFound.isNotEmpty) ...[
              const Text('Columns found:',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 4),
              Wrap(
                spacing: 4,
                runSpacing: 4,
                children: columnsFound.map((c) {
                  final isRequired = ['type', 'amount', 'date'].contains(c);
                  return Chip(
                    label: Text(c, style: const TextStyle(fontSize: 11)),
                    backgroundColor: isRequired
                        ? Colors.green.withValues(alpha: 0.1)
                        : Colors.grey.withValues(alpha: 0.1),
                    visualDensity: VisualDensity.compact,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    padding: EdgeInsets.zero,
                  );
                }).toList(),
              ),
            ],
            if (columnsMissing.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                'Optional columns not in file: ${columnsMissing.join(", ")}',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
            const SizedBox(height: 12),

            // Categories available
            if (categories.isNotEmpty) ...[
              const Text('Your categories:',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 4),
              Wrap(
                spacing: 4,
                runSpacing: 4,
                children: categories.take(12).map((c) {
                  final name = c['name'] ?? '';
                  final type = c['type'] ?? '';
                  return Chip(
                    label: Text('$name ($type)',
                        style: const TextStyle(fontSize: 11)),
                    visualDensity: VisualDensity.compact,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    padding: EdgeInsets.zero,
                  );
                }).toList(),
              ),
              if (categories.length > 12)
                Text('  +${categories.length - 12} more',
                    style: TextStyle(fontSize: 11, color: Colors.grey[600])),
            ],
            const SizedBox(height: 12),

            // Preview rows
            if (preview.isNotEmpty) ...[
              const Text('Preview (first 5 valid rows):',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
              const SizedBox(height: 4),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: preview.map((row) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 2),
                      child: Text(
                        'Row ${row['row']}: ${row['type']} | ${row['category_id']} | ${row['amount']} | ${row['date']}${row['description'] != null ? ' | ${row['description']}' : ''}',
                        style: const TextStyle(fontSize: 11, fontFamily: 'monospace'),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],
            const SizedBox(height: 12),

            // Errors
            if (errors.isNotEmpty) ...[
              Text(
                'Validation errors (${errors.length}${invalidRows > 10 ? ' of $invalidRows' : ''}):',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                  color: Colors.red[700],
                ),
              ),
              const SizedBox(height: 4),
              ...errors.take(10).map((e) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 1),
                    child: Text(
                      '  Row ${e['row']}: ${e['reason']}',
                      style: TextStyle(fontSize: 12, color: Colors.red[600]),
                    ),
                  )),
            ],
            const SizedBox(height: 16),

            // Import button
            if (validRows > 0)
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: _importing ? null : _confirmImport,
                  icon: _importing
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.check_circle),
                  label: Text('Import $validRows Transactions'),
                ),
              ),
            if (validRows == 0 && totalRows > 0)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'No valid rows found. Fix the errors above and try again.',
                        style: TextStyle(color: Colors.red),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _statChip(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(label,
              style: TextStyle(fontSize: 12, color: color, fontWeight: FontWeight.w500)),
          const SizedBox(width: 4),
          Text(value,
              style: TextStyle(fontSize: 14, color: color, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildResultCard(ThemeData theme) {
    final isError = _result!.startsWith('Error') || _result!.startsWith('Import error') || _result!.startsWith('Export error') || _result!.startsWith('Analysis failed');
    return Card(
      color: isError ? Colors.red.withValues(alpha: 0.05) : Colors.green.withValues(alpha: 0.05),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isError ? Icons.error_outline : Icons.check_circle_outline,
                  color: isError ? Colors.red : Colors.green,
                ),
                const SizedBox(width: 8),
                Text(
                  isError ? 'Error' : 'Result',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: isError ? Colors.red : Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            SelectableText(_result!, style: const TextStyle(fontSize: 13)),
          ],
        ),
      ),
    );
  }
}
