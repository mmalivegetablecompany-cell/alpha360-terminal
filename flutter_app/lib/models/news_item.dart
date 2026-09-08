class NewsItem {
  final String title;
  final String link;
  final String pubDate;
  final String query;
  final String sentiment; // BULLISH, BEARISH, NEUTRAL

  NewsItem({
    required this.title,
    required this.link,
    required this.pubDate,
    required this.query,
    required this.sentiment,
  });

  factory NewsItem.fromJson(Map<String, dynamic> json) {
    return NewsItem(
      title: json['title']?.toString() ?? '',
      link: json['link']?.toString() ?? '',
      pubDate: json['pub_date']?.toString() ?? '',
      query: json['query']?.toString() ?? '',
      sentiment: json['sentiment']?.toString() ?? 'NEUTRAL',
    );
  }
}
