import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/category_model.dart';
import '../../providers/currency_provider.dart';
import '../../widgets/error_view.dart';

/// Category Manager — adaptive maintenance feature.
/// Lets users add, rename, and delete their own income/expense categories
/// instead of being limited to the seeded defaults.
class CategoryManagerScreen extends ConsumerStatefulWidget {
  const CategoryManagerScreen({super.key});

  @override
  ConsumerState<CategoryManagerScreen> createState() =>
      _CategoryManagerScreenState();
}

class _CategoryManagerScreenState extends ConsumerState<CategoryManagerScreen> {
  String _filter = 'expense';
  bool _busy = false;

  Future<void> _addCategory() async {
    final nameController = TextEditingController();
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Add ${_filter == 'income' ? 'Income' : 'Expense'} Category'),
        content: TextField(
          controller: nameController,
          autofocus: true,
          decoration: const InputDecoration(
            labelText: 'Category name',
            border: OutlineInputBorder(),
          ),
          onSubmitted: (v) => Navigator.pop(ctx, v.trim()),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, nameController.text.trim()),
            child: const Text('Add'),
          ),
        ],
      ),
    );
    if (result == null || result.isEmpty) return;

    setState(() => _busy = true);
    try {
      await ref.read(categoryServiceProvider).addCategory(result, _filter);
      _refreshProviders();
      _snack('Category "$result" added');
    } catch (e) {
      _snack('Failed to add: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _renameCategory(CategoryModel cat) async {
    final nameController = TextEditingController(text: cat.name);
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Rename Category'),
        content: TextField(
          controller: nameController,
          autofocus: true,
          decoration: const InputDecoration(
            labelText: 'New name',
            border: OutlineInputBorder(),
          ),
          onSubmitted: (v) => Navigator.pop(ctx, v.trim()),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, nameController.text.trim()),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (result == null || result.isEmpty || result == cat.name) return;

    setState(() => _busy = true);
    try {
      await ref.read(categoryServiceProvider).updateCategory(cat.id, result);
      _refreshProviders();
      _snack('Renamed to "$result"');
    } catch (e) {
      _snack('Failed to rename: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _deleteCategory(CategoryModel cat) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Category'),
        content: Text(
            'Delete "${cat.name}"?\n\nThis is only possible if no transactions use it.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (confirm != true) return;

    setState(() => _busy = true);
    try {
      await ref.read(categoryServiceProvider).deleteCategory(cat.id);
      _refreshProviders();
      _snack('Category "${cat.name}" deleted');
    } catch (e) {
      _snack('Cannot delete: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  /// Invalidate every category cache so all dropdowns refresh immediately.
  void _refreshProviders() {
    ref.invalidate(categoriesProvider);
    ref.invalidate(incomeCategoriesProvider);
    ref.invalidate(expenseCategoriesProvider);
  }

  void _snack(String msg) {
    if (mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(msg)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider =
        _filter == 'income' ? incomeCategoriesProvider : expenseCategoriesProvider;
    final categoriesAsync = ref.watch(provider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Manage Categories'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _busy ? null : _addCategory,
        icon: const Icon(Icons.add),
        label: const Text('Add'),
      ),
      body: Column(
        children: [
          // Type filter
          Padding(
            padding: const EdgeInsets.all(16),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                    value: 'expense',
                    label: Text('Expense'),
                    icon: Icon(Icons.arrow_upward)),
                ButtonSegment(
                    value: 'income',
                    label: Text('Income'),
                    icon: Icon(Icons.arrow_downward)),
              ],
              selected: {_filter},
              onSelectionChanged: (v) => setState(() => _filter = v.first),
            ),
          ),
          Expanded(
            child: categoriesAsync.when(
              data: (categories) {
                if (categories.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.category_outlined,
                            size: 64, color: Colors.grey[300]),
                        const SizedBox(height: 12),
                        Text('No ${_filter == 'income' ? 'income' : 'expense'} categories',
                            style: TextStyle(color: Colors.grey[600])),
                      ],
                    ),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () async => _refreshProviders(),
                  child: ListView.builder(
                    physics: const AlwaysScrollableScrollPhysics(),
                    itemCount: categories.length,
                    itemBuilder: (context, i) {
                      final cat = categories[i];
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: _filter == 'income'
                              ? Colors.green.withValues(alpha: 0.15)
                              : theme.colorScheme.primary.withValues(alpha: 0.15),
                          child: Icon(
                            _filter == 'income'
                                ? Icons.arrow_downward
                                : Icons.arrow_upward,
                            size: 18,
                            color: _filter == 'income'
                                ? Colors.green[700]
                                : theme.colorScheme.primary,
                          ),
                        ),
                        title: Text(cat.name),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.edit_outlined, size: 20),
                              tooltip: 'Rename',
                              onPressed: _busy ? null : () => _renameCategory(cat),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline,
                                  size: 20, color: Colors.red),
                              tooltip: 'Delete',
                              onPressed: _busy ? null : () => _deleteCategory(cat),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => ErrorView(
                message: 'Could not load categories',
                onRetry: _refreshProviders,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
