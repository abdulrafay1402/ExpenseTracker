import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/currency_model.dart';
import '../models/category_model.dart';
import '../services/currency_service.dart';
import '../services/category_service.dart';

final currencyServiceProvider = Provider((ref) => CurrencyService());
final categoryServiceProvider = Provider((ref) => CategoryService());

// Currencies provider
final currenciesProvider = FutureProvider<List<CurrencyModel>>((ref) async {
  final service = ref.watch(currencyServiceProvider);
  return service.getCurrencies();
});

// Categories provider (all)
final categoriesProvider = FutureProvider<List<CategoryModel>>((ref) async {
  final service = ref.watch(categoryServiceProvider);
  return service.listCategories();
});

// Income categories provider
final incomeCategoriesProvider = FutureProvider<List<CategoryModel>>((ref) async {
  final service = ref.watch(categoryServiceProvider);
  return service.listCategories(type: 'income');
});

// Expense categories provider
final expenseCategoriesProvider = FutureProvider<List<CategoryModel>>((ref) async {
  final service = ref.watch(categoryServiceProvider);
  return service.listCategories(type: 'expense');
});
