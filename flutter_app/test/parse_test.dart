import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:indian_stock_terminal/models/stock.dart';
import 'package:indian_stock_terminal/services/market_service.dart';

void main() {
  test('Test parsing advanced_technicals_424.json', () {
    final techFile = File('d:/New folder (5)/database/advanced_technicals_424.json');
    expect(techFile.existsSync(), isTrue);
    final techStr = techFile.readAsStringSync();

    final fundFile = File('d:/New folder (5)/database/html_424_stocks.json');
    expect(fundFile.existsSync(), isTrue);
    final fundStr = fundFile.readAsStringSync();

    print('Tech string length: ${techStr.length}');
    print('Fund string length: ${fundStr.length}');

    final techList = json.decode(techStr) as List<dynamic>;
    print('Decoded tech count: ${techList.length}');

    final stocks = <Stock>[];
    for (int i = 0; i < techList.length; i++) {
      try {
        final s = Stock.fromJson(Map<String, dynamic>.from(techList[i] as Map));
        stocks.add(s);
      } catch (e, st) {
        print('Error parsing stock at index $i (${techList[i]['symbol']}): $e\n$st');
        rethrow;
      }
    }
    print('Successfully parsed ${stocks.length} stocks!');
    expect(stocks.length, equals(424));
  });
}
