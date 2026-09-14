import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/currency_model.dart';
import 'api_client.dart';

class CurrencyService {
  final Dio _dio = ApiClient.dio;

  Future<List<CurrencyModel>> getCurrencies() async {
    try {
      final res = await _dio.get(ApiConfig.currencies);
      final map = res.data['currencies'] as Map<String, dynamic>;
      return map.entries
          .map((e) => CurrencyModel(code: e.key, name: e.value as String))
          .toList()
        ..sort((a, b) => a.code.compareTo(b.code));
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }

  Future<RateModel> getRate(String base, String target) async {
    try {
      final res = await _dio.get(ApiConfig.currencyRate, queryParameters: {
        'base': base,
        'target': target,
      });
      return RateModel.fromJson(res.data);
    } on DioException catch (e) {
      throw ApiException(extractErrorMessage(e), statusCode: e.response?.statusCode);
    }
  }
}
