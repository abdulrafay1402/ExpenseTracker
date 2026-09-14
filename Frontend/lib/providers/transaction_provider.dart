import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/transaction_model.dart';
import '../services/transaction_service.dart';

final transactionServiceProvider = Provider((ref) => TransactionService());

class TransactionState {
  final List<TransactionModel> transactions;
  final bool isLoading;
  final String? error;

  const TransactionState({
    this.transactions = const [],
    this.isLoading = false,
    this.error,
  });

  TransactionState copyWith({
    List<TransactionModel>? transactions,
    bool? isLoading,
    String? error,
  }) {
    return TransactionState(
      transactions: transactions ?? this.transactions,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class TransactionNotifier extends Notifier<TransactionState> {
  late final TransactionService _service;

  @override
  TransactionState build() {
    _service = ref.watch(transactionServiceProvider);
    return const TransactionState();
  }

  Future<void> loadTransactions({
    String? type,
    int? categoryId,
    String? startDate,
    String? endDate,
    String? search,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final list = await _service.listTransactions(
        type: type,
        categoryId: categoryId,
        startDate: startDate,
        endDate: endDate,
        search: search,
      );
      state = state.copyWith(transactions: list, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  /// Add a transaction. Rethrows on failure so the caller can react.
  Future<void> addTransaction(Map<String, dynamic> data) async {
    state = state.copyWith(error: null); // clear previous error
    try {
      await _service.addTransaction(data);
      // Reload list to include the new transaction
      await loadTransactions();
    } catch (e) {
      state = state.copyWith(error: e.toString());
      rethrow; // let the screen know it failed
    }
  }

  Future<void> updateTransaction(int id, Map<String, dynamic> data) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _service.updateTransaction(id, data);
      await loadTransactions();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> voidTransaction(int id) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _service.voidTransaction(id);
      await loadTransactions();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final transactionProvider =
    NotifierProvider<TransactionNotifier, TransactionState>(TransactionNotifier.new);
