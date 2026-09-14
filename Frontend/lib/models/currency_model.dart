class CurrencyModel {
  final String code;
  final String name;

  CurrencyModel({required this.code, required this.name});
}

class RateModel {
  final String base;
  final String target;
  final double rate;

  RateModel({required this.base, required this.target, required this.rate});

  factory RateModel.fromJson(Map<String, dynamic> json) {
    return RateModel(
      base: json['base'] as String,
      target: json['target'] as String,
      rate: (json['rate'] as num).toDouble(),
    );
  }
}
