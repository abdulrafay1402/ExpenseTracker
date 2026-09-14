import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../models/transaction_model.dart';
import '../../services/transaction_service.dart';
import '../../providers/transaction_provider.dart';

class TransactionDetailScreen extends ConsumerStatefulWidget {
  final int id;
  const TransactionDetailScreen({super.key, required this.id});

  @override
  ConsumerState<TransactionDetailScreen> createState() => _TransactionDetailScreenState();
}

class _TransactionDetailScreenState extends ConsumerState<TransactionDetailScreen> {
  TransactionModel? _tx;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final service = TransactionService();
      final tx = await service.getTransaction(widget.id);
      setState(() {
        _tx = tx;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _voidTransaction() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Void Transaction'),
        content: const Text('This will soft-delete the transaction. Continue?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Void')),
        ],
      ),
    );
    if (confirm != true) return;
    await ref.read(transactionProvider.notifier).voidTransaction(widget.id);
    if (context.mounted) context.pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Transaction Detail'),
        actions: [
          if (_tx != null && _tx!.voided == 0)
            IconButton(
              icon: const Icon(Icons.delete_outline),
              onPressed: _voidTransaction,
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.cloud_off, size: 48, color: Colors.grey[400]),
                        const SizedBox(height: 12),
                        Text('Could not load transaction',
                            style: TextStyle(color: Colors.grey[600])),
                        const SizedBox(height: 12),
                        FilledButton.icon(
                          onPressed: _load,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : _tx == null
                  ? const Center(child: Text('Not found'))
                  : ListView(
                      padding: const EdgeInsets.all(16),
                      children: [
                        _infoRow('Type', _tx!.type.toUpperCase()),
                        _infoRow(
                            'Amount',
                            '${NumberFormat.currency(symbol: '${_tx!.currency} ').format(_tx!.amount)}'),
                        _infoRow('Date',
                            DateFormat('MMM dd, yyyy').format(DateTime.parse(_tx!.date))),
                        _infoRow('Description', _tx!.description ?? '—'),
                        _infoRow('Rate to Base', _tx!.rateToBase.toString()),
                        _infoRow('Status', _tx!.voided == 1 ? 'VOIDED' : 'Active'),
                      ],
                    ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label,
                style: TextStyle(color: Colors.grey[600], fontWeight: FontWeight.w500)),
          ),
          Expanded(child: Text(value, style: const TextStyle(fontWeight: FontWeight.w600))),
        ],
      ),
    );
  }
}
