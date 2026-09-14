import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/transaction_model.dart';
import 'api_client.dart';

class TransactionService {
  final Dio _dio = ApiClient.dio;

  Future<TransactionModel> addTransaction(Map<String, dynamic> data) async {
    try {
      final res = await _dio.post(ApiConfig.transactions, data: data);
      return TransactionModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<List<TransactionModel>> listTransactions({
    String? type,
    int? categoryId,
    String? startDate,
    String? endDate,
    String? search,
  }) async {
    try {
      final params = <String, dynamic>{};
      if (type != null) params['type'] = type;
      if (categoryId != null) params['category_id'] = categoryId;
      if (startDate != null) params['start_date'] = startDate;
      if (endDate != null) params['end_date'] = endDate;
      if (search != null) params['search'] = search;

      final res = await _dio.get(ApiConfig.transactions, queryParameters: params);
      return (res.data as List).map((e) => TransactionModel.fromJson(e)).toList();
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<TransactionModel> getTransaction(int id) async {
    try {
      final res = await _dio.get('${ApiConfig.transactions}/$id');
      return TransactionModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<TransactionModel> updateTransaction(int id, Map<String, dynamic> data) async {
    try {
      final res = await _dio.put('${ApiConfig.transactions}/$id', data: data);
      return TransactionModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<TransactionModel> voidTransaction(int id) async {
    try {
      final res = await _dio.delete('${ApiConfig.transactions}/$id');
      return TransactionModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }
}
