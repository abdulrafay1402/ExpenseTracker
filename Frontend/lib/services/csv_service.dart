import 'package:dio/dio.dart';
import 'package:http_parser/http_parser.dart';
import '../config/api_config.dart';
import 'api_client.dart';

class CsvService {
  final Dio _dio = ApiClient.dio;

  /// Analyze CSV structure without importing (preview & validation).
  Future<Map<String, dynamic>> analyzeCsv(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          filePath,
          contentType: MediaType('text', 'csv'),
        ),
      });
      final res = await _dio.post(ApiConfig.csvAnalyze, data: formData);
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<Map<String, dynamic>> importCsv(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          filePath,
          contentType: MediaType('text', 'csv'),
        ),
      });
      final res = await _dio.post(ApiConfig.csvImport, data: formData);
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<String> exportCsv() async {
    try {
      final res = await _dio.get(
        ApiConfig.csvExport,
        options: Options(responseType: ResponseType.plain),
      );
      return res.data as String;
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<Map<String, dynamic>> getGuidelines() async {
    try {
      final res = await _dio.get(ApiConfig.csvGuidelines);
      return res.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }
}
