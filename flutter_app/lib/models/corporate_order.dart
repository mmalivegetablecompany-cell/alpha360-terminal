class CorporateOrder {
  final String symbol;
  final String category; // MAJOR ORDER WIN, CAPEX EXPANSION, DIVIDEND / BONUS, etc.
  final String headline;
  final String dateTime;
  final String attachment;

  CorporateOrder({
    required this.symbol,
    required this.category,
    required this.headline,
    required this.dateTime,
    required this.attachment,
  });

  factory CorporateOrder.fromJson(Map<String, dynamic> json) {
    return CorporateOrder(
      symbol: json['symbol']?.toString() ?? '',
      category: json['category']?.toString() ?? 'CORPORATE FILING',
      headline: json['headline']?.toString() ?? '',
      dateTime: json['date_time']?.toString() ?? '',
      attachment: json['attachment']?.toString() ?? '',
    );
  }
}
