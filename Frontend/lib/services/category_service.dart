import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/category_model.dart';
import 'api_client.dart';

class CategoryService {
  final Dio _dio = ApiClient.dio;

  Future<List<CategoryModel>> listCategories({String? type}) async {
    try {
      final params = <String, dynamic>{};
      if (type != null) params['type'] = type;
      final res = await _dio.get(ApiConfig.categories, queryParameters: params);
      return (res.data as List).map((e) => CategoryModel.fromJson(e)).toList();
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<CategoryModel> addCategory(String name, String type) async {
    try {
      final res = await _dio.post(ApiConfig.categories, data: {'name': name, 'type': type});
      return CategoryModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<CategoryModel> updateCategory(int id, String name) async {
    try {
      final res = await _dio.put('${ApiConfig.categories}/$id', data: {'name': name});
      return CategoryModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<void> deleteCategory(int id) async {
    try {
      await _dio.delete('${ApiConfig.categories}/$id');
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }
}
