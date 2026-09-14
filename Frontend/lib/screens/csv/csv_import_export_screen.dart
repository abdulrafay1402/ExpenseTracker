import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:intl/intl.dart';
import '../../services/csv_service.dart';

class CsvImportExportScreen extends StatefulWidget {
  const CsvImportExportScreen({super.key});

  @override
  State<CsvImportExportScreen> createState() => _CsvImportExportScreenState();
}

class _CsvImportExportScreenState extends State<CsvImportExportScreen> {
  final _csvService = CsvService();
  bool _importing = false;
  bool _exporting = false;
  String? _result;

  Future<void> _importCsv() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['csv'],
    );
    if (result.isEmpty) return;
    final filePath = result.first.path;
    if (filePath == null) return;

    setState(() {
      _importing = true;
      _result = null;
    });

    try {
      final res = await _csvService.importCsv(filePath);
      final imported = res['imported'];
      final failed = res['failed'] as List?;
      setState(() {
        _result = 'Imported: $imported, Failed: ${failed?.length ?? 0}';
        if (failed != null && failed.isNotEmpty) {
          _result =
              '$_result\n\nFailed rows:\n${failed.map((f) => 'Row ${f['row']}: ${f['reason']}').join('\n')}';
        }
      });
    } catch (e) {
      setState(() => _result = 'Error: $e');
    } finally {
      setState(() => _importing = false);
    }
  }

  Future<void> _exportCsv() async {
    setState(() {
      _exporting = true;
      _result = null;
    });

    try {
      final csvContent = await _csvService.exportCsv();
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final fileName = 'expense_mate_$timestamp.csv';

      final csvBytes = Uint8List.fromList(utf8.encode(csvContent));

      // Use FilePicker.saveFile() — opens the system "Save As" dialog
      // so the user picks where to store the file (Downloads, Documents, etc.)
      final savedUri = await FilePicker.saveFile(
        dialogTitle: 'Save CSV Export',
        fileName: fileName,
        bytes: csvBytes,
        type: FileType.custom,
        allowedExtensions: ['csv'],
      );

      if (savedUri == null) {
        // User cancelled
        setState(() => _result = 'Export cancelled.');
        return;
      }

      // Write the CSV content to the user-chosen location
      final file = File.fromUri(savedUri);
      await file.writeAsBytes(csvBytes);

      setState(() {
        _result = 'Exported successfully!\n\nSaved to:\n${savedUri.path}\n\n'
            'You can find this file in your file manager and use it for import.';
      });
    } catch (e) {
      setState(() => _result = 'Error: $e');
    } finally {
      setState(() => _exporting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('CSV Import / Export')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Import transactions from a CSV file or export all your transactions.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            Text(
              'Export saves to a location you choose (Downloads, Documents, etc.) so you can easily find and re-import it later.',
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            OutlinedButton.icon(
              onPressed: _importing ? null : _importCsv,
              icon: const Icon(Icons.upload_file),
              label: _importing
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Import CSV'),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: _exporting ? null : _exportCsv,
              icon: const Icon(Icons.download),
              label: _exporting
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Export CSV'),
            ),
            const SizedBox(height: 24),
            if (_result != null)
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: SingleChildScrollView(
                      child: SelectableText(_result!),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
