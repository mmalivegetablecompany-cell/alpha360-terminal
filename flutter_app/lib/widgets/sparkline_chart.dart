import 'package:flutter/material.dart';
import '../models/stock.dart';

class SparklineChart extends StatelessWidget {
  final List<CandleData> candles;
  final Color color;
  final double width;
  final double height;
  final bool showFill;

  const SparklineChart({
    super.key,
    required this.candles,
    required this.color,
    this.width = 60,
    this.height = 24,
    this.showFill = true,
  });

  @override
  Widget build(BuildContext context) {
    if (candles.isEmpty) {
      return SizedBox(width: width, height: height);
    }

    return SizedBox(
      width: width,
      height: height,
      child: CustomPaint(
        painter: _SparklinePainter(
          prices: candles.map((c) => c.close).toList(),
          lineColor: color,
          showFill: showFill,
        ),
      ),
    );
  }
}

class _SparklinePainter extends CustomPainter {
  final List<double> prices;
  final Color lineColor;
  final bool showFill;

  _SparklinePainter({
    required this.prices,
    required this.lineColor,
    required this.showFill,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (prices.length < 2) return;

    double min = prices.first;
    double max = prices.first;
    for (final p in prices) {
      if (p < min) min = p;
      if (p > max) max = p;
    }

    final range = (max - min) == 0 ? 1.0 : (max - min);
    final points = <Offset>[];
    final stepX = size.width / (prices.length - 1);

    for (int i = 0; i < prices.length; i++) {
      final x = i * stepX;
      final normalizedY = (prices[i] - min) / range;
      final y = size.height - (normalizedY * (size.height - 4)) - 2;
      points.add(Offset(x, y));
    }

    final path = Path();
    path.moveTo(points.first.dx, points.first.dy);
    for (int i = 1; i < points.length; i++) {
      final p0 = points[i - 1];
      final p1 = points[i];
      final controlPointX = (p0.dx + p1.dx) / 2;
      path.cubicTo(controlPointX, p0.dy, controlPointX, p1.dy, p1.dx, p1.dy);
    }

    if (showFill) {
      final fillPath = Path.from(path);
      fillPath.lineTo(points.last.dx, size.height);
      fillPath.lineTo(points.first.dx, size.height);
      fillPath.close();

      final fillPaint = Paint()
        ..shader = LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            lineColor.withAlpha(50),
            lineColor.withAlpha(0),
          ],
        ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
        ..style = PaintingStyle.fill;

      canvas.drawPath(fillPath, fillPaint);
    }

    final linePaint = Paint()
      ..color = lineColor
      ..strokeWidth = 1.6
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    canvas.drawPath(path, linePaint);
  }

  @override
  bool shouldRepaint(covariant _SparklinePainter oldDelegate) {
    return oldDelegate.prices != prices || oldDelegate.lineColor != lineColor;
  }
}
