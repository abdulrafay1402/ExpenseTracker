import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/budget_model.dart';
import 'api_client.dart';

class BudgetService {
  final Dio _dio = ApiClient.dio;

  Future<BudgetModel> setBudget(Map<String, dynamic> data) async {
    try {
      final res = await _dio.post(ApiConfig.budget, data: data);
      return BudgetModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<List<BudgetModel>> listBudgets({int? month, int? year}) async {
    try {
      final params = <String, dynamic>{};
      if (month != null) params['month'] = month;
      if (year != null) params['year'] = year;
      final res = await _dio.get(ApiConfig.budget, queryParameters: params);
      return (res.data as List).map((e) => BudgetModel.fromJson(e)).toList();
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<BudgetModel> updateBudget(int id, {double? amount, double? alertThreshold}) async {
    try {
      final data = <String, dynamic>{};
      if (amount != null) data['amount'] = amount;
      if (alertThreshold != null) data['alert_threshold'] = alertThreshold;
      final res = await _dio.put('${ApiConfig.budget}/$id', data: data);
      return BudgetModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<AlertModel> checkAlert(int categoryId, {int? month, int? year}) async {
    try {
      final params = <String, dynamic>{};
      if (month != null) params['month'] = month;
      if (year != null) params['year'] = year;
      final res = await _dio.get(
        '${ApiConfig.budget}/alert/$categoryId',
        queryParameters: params,
      );
      return AlertModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<List<AlertModel>> checkAllAlerts({int? month, int? year}) async {
    try {
      final params = <String, dynamic>{};
      if (month != null) params['month'] = month;
      if (year != null) params['year'] = year;
      final res = await _dio.get(ApiConfig.budgetAlerts, queryParameters: params);
      return (res.data as List).map((e) => AlertModel.fromJson(e)).toList();
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }
}
