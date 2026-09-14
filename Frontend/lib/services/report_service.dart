import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/report_model.dart';
import 'api_client.dart';

class ReportService {
  final Dio _dio = ApiClient.dio;

  Future<DashboardModel> getDashboard({int? month, int? year}) async {
    try {
      final params = <String, dynamic>{};
      if (month != null) params['month'] = month;
      if (year != null) params['year'] = year;
      final res = await _dio.get(ApiConfig.dashboard, queryParameters: params);
      return DashboardModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<CategoryWiseReport> getCategoryWise({int? month, int? year}) async {
    try {
      final params = <String, dynamic>{};
      if (month != null) params['month'] = month;
      if (year != null) params['year'] = year;
      final res = await _dio.get(ApiConfig.categoryWise, queryParameters: params);
      return CategoryWiseReport.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<MonthlyTrendReport> getMonthlyTrend({int? year}) async {
    try {
      final params = <String, dynamic>{};
      if (year != null) params['year'] = year;
      final res = await _dio.get(ApiConfig.monthlyTrend, queryParameters: params);
      return MonthlyTrendReport.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<IncomeVsExpenseReport> getIncomeVsExpense({int? year}) async {
    try {
      final params = <String, dynamic>{};
      if (year != null) params['year'] = year;
      final res = await _dio.get(ApiConfig.incomeVsExpense, queryParameters: params);
      return IncomeVsExpenseReport.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<MonthlySummary> getMonthlySummary({int? month, int? year}) async {
    try {
      final params = <String, dynamic>{};
      if (month != null) params['month'] = month;
      if (year != null) params['year'] = year;
      final res = await _dio.get(ApiConfig.monthlySummary, queryParameters: params);
      return MonthlySummary.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }
}
