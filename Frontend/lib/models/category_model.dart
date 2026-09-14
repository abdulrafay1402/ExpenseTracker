class CategoryModel {
  final int id;
  final String userId;
  final String name;
  final String type; // income or expense

  CategoryModel({
    required this.id,
    required this.userId,
    required this.name,
    required this.type,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['id'] as int,
      userId: json['user_id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'type': type,
    };
  }
}
