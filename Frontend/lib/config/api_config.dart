class ApiConfig {
  /// Change this single value to point to a different backend.
  /// When deployed, replace with your cloud URL (e.g. https://api.expensemate.com)
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  // Transaction endpoints
  static const String transactions = '/transactions';

  // Category endpoints
  static const String categories = '/categories';

  // Budget endpoints
  static const String budget = '/budget';
  static const String budgetAlerts = '/budget/alerts';

  // Report endpoints
  static const String dashboard = '/reports/dashboard';
  static const String categoryWise = '/reports/category-wise';
  static const String monthlyTrend = '/reports/monthly';
  static const String incomeVsExpense = '/reports/income-vs-expense';
  static const String monthlySummary = '/reports/monthly-summary';

  // Currency endpoints
  static const String currencies = '/currencies';
  static const String currencyRate = '/currencies/rate';

  // CSV endpoints
  static const String csvImport = '/csv/import';
  static const String csvExport = '/csv/export';

  // Backup endpoints
  static const String backup = '/backup';
  static const String backupRestore = '/backup/restore';
}
