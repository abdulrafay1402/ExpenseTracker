import 'package:dio/dio.dart';
import '../config/api_config.dart';

class ApiClient {
  static final Dio _dio = Dio(BaseOptions(
    baseUrl: ApiConfig.baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {'Content-Type': 'application/json'},
  ));

  static Dio get dio => _dio;
}

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

/// Helper to extract error message from Dio responses.
String extractErrorMessage(DioException e) {
  if (e.response?.data != null) {
    final data = e.response!.data;
    if (data is Map && data.containsKey('detail')) {
      return data['detail'].toString();
    }
    return data.toString();
  }
  return e.message ?? 'Unknown error';
}
