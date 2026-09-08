class CustomBasket {
  final String id;
  String name;
  String desc;
  List<String> symbols;

  CustomBasket({
    required this.id,
    required this.name,
    this.desc = '',
    required this.symbols,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'desc': desc,
        'symbols': symbols,
      };

  factory CustomBasket.fromJson(Map<String, dynamic> json) => CustomBasket(
        id: json['id']?.toString() ?? '',
        name: json['name']?.toString() ?? 'Custom Basket',
        desc: json['desc']?.toString() ?? '',
        symbols: (json['symbols'] as List<dynamic>?)?.map((s) => s.toString()).toList() ?? [],
      );
}
