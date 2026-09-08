import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

// ============================================================================
// 1. PRICE FLASH TEXT WIDGET
// Flashes subtle green/red background highlight when price changes, then fades
// ============================================================================
class PriceFlashText extends StatefulWidget {
  final double value;
  final String formattedText;
  final TextStyle? style;
  final bool isPercentage;
  final TextAlign textAlign;
  final EdgeInsets padding;

  const PriceFlashText({
    super.key,
    required this.value,
    required this.formattedText,
    this.style,
    this.isPercentage = false,
    this.textAlign = TextAlign.end,
    this.padding = const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
  });

  @override
  State<PriceFlashText> createState() => _PriceFlashTextState();
}

class _PriceFlashTextState extends State<PriceFlashText> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  Color? _flashColor;
  double _lastValue = 0.0;

  @override
  void initState() {
    super.initState();
    _lastValue = widget.value;
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 750),
    );
    _animation = CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic);
  }

  @override
  void didUpdateWidget(covariant PriceFlashText oldWidget) {
    super.didUpdateWidget(oldWidget);
    if ((widget.value - _lastValue).abs() > 0.001) {
      final isUp = widget.value > _lastValue;
      _lastValue = widget.value;
      _flashColor = isUp ? const Color(0xFF00E676) : const Color(0xFFFF334B);
      _controller.forward(from: 0.0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        final currentFlash = _flashColor;
        Color? bgColor;
        if (currentFlash != null && _controller.isAnimating) {
          final alpha = ((1.0 - _animation.value) * 55).round().clamp(0, 255);
          bgColor = currentFlash.withAlpha(alpha);
        }

        return Container(
          padding: widget.padding,
          decoration: BoxDecoration(
            color: bgColor ?? Colors.transparent,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            widget.formattedText,
            textAlign: widget.textAlign,
            style: widget.style,
          ),
        );
      },
    );
  }
}

// ============================================================================
// 2. INTERACTIVE SCALE CARD
// Tactile micro-scale reduction on press (0.985) & hover lift (1.01) on web/desktop
// ============================================================================
class InteractiveScaleCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final BorderRadius? borderRadius;
  final Color? hoverBorderColor;
  final EdgeInsetsGeometry? margin;

  const InteractiveScaleCard({
    super.key,
    required this.child,
    this.onTap,
    this.onLongPress,
    this.borderRadius,
    this.hoverBorderColor,
    this.margin,
  });

  @override
  State<InteractiveScaleCard> createState() => _InteractiveScaleCardState();
}

class _InteractiveScaleCardState extends State<InteractiveScaleCard> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
      reverseDuration: const Duration(milliseconds: 140),
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.985).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOutCubic),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final br = widget.borderRadius ?? BorderRadius.circular(12);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      cursor: widget.onTap != null ? SystemMouseCursors.click : SystemMouseCursors.basic,
      child: GestureDetector(
        onTapDown: (_) => _controller.forward(),
        onTapUp: (_) => _controller.reverse(),
        onTapCancel: () => _controller.reverse(),
        onTap: widget.onTap,
        onLongPress: widget.onLongPress,
        child: AnimatedBuilder(
          animation: _scaleAnimation,
          builder: (context, child) {
            final hoverScale = _isHovered && !_controller.isAnimating && _controller.value == 0.0 ? 1.008 : 1.0;
            return Transform.scale(
              scale: _scaleAnimation.value * hoverScale,
              child: child,
            );
          },
          child: Container(
            margin: widget.margin,
            decoration: BoxDecoration(
              borderRadius: br,
              border: _isHovered && widget.hoverBorderColor != null
                  ? Border.all(color: widget.hoverBorderColor!, width: 1.2)
                  : null,
            ),
            child: widget.child,
          ),
        ),
      ),
    );
  }
}

// ============================================================================
// 3. PULSE GLOW DOT WIDGET
// Live status indicator with expanding ripple ring wave
// ============================================================================
class PulseGlowDot extends StatefulWidget {
  final Color color;
  final double size;
  final bool isPulsing;

  const PulseGlowDot({
    super.key,
    required this.color,
    this.size = 8.0,
    this.isPulsing = true,
  });

  @override
  State<PulseGlowDot> createState() => _PulseGlowDotState();
}

class _PulseGlowDotState extends State<PulseGlowDot> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _ringAnimation;
  late Animation<double> _alphaAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1800),
    );

    _ringAnimation = Tween<double>(begin: 1.0, end: 2.8).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutQuad),
    );

    _alphaAnimation = Tween<double>(begin: 0.6, end: 0.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutQuad),
    );

    if (widget.isPulsing) {
      _controller.repeat();
    }
  }

  @override
  void didUpdateWidget(covariant PulseGlowDot oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isPulsing && !_controller.isAnimating) {
      _controller.repeat();
    } else if (!widget.isPulsing && _controller.isAnimating) {
      _controller.stop();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size * 2.8,
      height: widget.size * 2.8,
      child: Stack(
        alignment: Alignment.center,
        children: [
          if (widget.isPulsing)
            AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                return Transform.scale(
                  scale: _ringAnimation.value,
                  child: Container(
                    width: widget.size,
                    height: widget.size,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: widget.color.withAlpha((_alphaAnimation.value * 255).round()),
                    ),
                  ),
                );
              },
            ),
          // Core solid dot
          Container(
            width: widget.size,
            height: widget.size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: widget.color,
              boxShadow: [
                BoxShadow(
                  color: widget.color.withAlpha(150),
                  blurRadius: 6,
                  spreadRadius: 1,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// 4. ANIMATED FAVORITE STAR
// Tactile spring pop animation on star click (0.8 -> 1.35 -> 1.0)
// ============================================================================
class AnimatedFavoriteStar extends StatefulWidget {
  final bool isFavorite;
  final VoidCallback onTap;
  final double size;

  const AnimatedFavoriteStar({
    super.key,
    required this.isFavorite,
    required this.onTap,
    this.size = 20.0,
  });

  @override
  State<AnimatedFavoriteStar> createState() => _AnimatedFavoriteStarState();
}

class _AnimatedFavoriteStarState extends State<AnimatedFavoriteStar> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 320),
    );

    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 0.75).chain(CurveTween(curve: Curves.easeIn)), weight: 25),
      TweenSequenceItem(tween: Tween(begin: 0.75, end: 1.35).chain(CurveTween(curve: Curves.easeOutBack)), weight: 45),
      TweenSequenceItem(tween: Tween(begin: 1.35, end: 1.0).chain(CurveTween(curve: Curves.easeInOut)), weight: 30),
    ]).animate(_controller);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTap() {
    _controller.forward(from: 0.0);
    widget.onTap();
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      iconSize: widget.size,
      padding: EdgeInsets.zero,
      constraints: const BoxConstraints(),
      splashRadius: widget.size + 4,
      onPressed: _handleTap,
      icon: ScaleTransition(
        scale: _scaleAnimation,
        child: Icon(
          widget.isFavorite ? Icons.star_rounded : Icons.star_outline_rounded,
          color: widget.isFavorite ? AppTheme.amberGold : AppColors.textMuted(context),
          size: widget.size,
        ),
      ),
    );
  }
}

// ============================================================================
// 5. SHIMMER SKELETON LOADER
// High-performance animated gradient sweep skeleton for loading states
// ============================================================================
class ShimmerLoadingList extends StatefulWidget {
  final int itemCount;

  const ShimmerLoadingList({super.key, this.itemCount = 6});

  @override
  State<ShimmerLoadingList> createState() => _ShimmerLoadingListState();
}

class _ShimmerLoadingListState extends State<ShimmerLoadingList> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = AppColors.isDark(context);
    final baseColor = isDark ? const Color(0xFF131D31) : const Color(0xFFE2E8F0);
    final highlightColor = isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9);

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return ListView.separated(
          padding: const EdgeInsets.all(14),
          itemCount: widget.itemCount,
          separatorBuilder: (_, __) => const SizedBox(height: 10),
          itemBuilder: (context, index) {
            return Container(
              height: 72,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: baseColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isDark ? const Color(0xFF1E293B) : const Color(0xFFCBD5E1),
                  width: 0.8,
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 22,
                    height: 22,
                    decoration: BoxDecoration(shape: BoxShape.circle, color: highlightColor),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 90,
                          height: 14,
                          decoration: BoxDecoration(
                            color: highlightColor,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          width: 180,
                          height: 10,
                          decoration: BoxDecoration(
                            color: highlightColor,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    width: 60,
                    height: 22,
                    decoration: BoxDecoration(
                      color: highlightColor,
                      borderRadius: BorderRadius.circular(6),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}

// ============================================================================
// 6. RADAR SCANNER SWEEP CANVAS
// Institutional circular radar sweep animation with rotating beam & blips
// ============================================================================
class RadarScannerSweep extends StatefulWidget {
  final double size;
  final Color beamColor;

  const RadarScannerSweep({
    super.key,
    this.size = 56.0,
    this.beamColor = const Color(0xFF00E676),
  });

  @override
  State<RadarScannerSweep> createState() => _RadarScannerSweepState();
}

class _RadarScannerSweepState extends State<RadarScannerSweep> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return CustomPaint(
          size: Size(widget.size, widget.size),
          painter: _RadarPainter(
            angle: _controller.value * 2 * math.pi,
            color: widget.beamColor,
          ),
        );
      },
    );
  }
}

class _RadarPainter extends CustomPainter {
  final double angle;
  final Color color;

  _RadarPainter({required this.angle, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;

    // Rings
    final ringPaint = Paint()
      ..color = color.withAlpha(40)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;

    canvas.drawCircle(center, radius * 0.35, ringPaint);
    canvas.drawCircle(center, radius * 0.70, ringPaint);
    canvas.drawCircle(center, radius - 1, ringPaint);

    // Crosshairs
    final crossPaint = Paint()
      ..color = color.withAlpha(30)
      ..strokeWidth = 0.8;
    canvas.drawLine(Offset(center.dx, 0), Offset(center.dx, size.height), crossPaint);
    canvas.drawLine(Offset(0, center.dy), Offset(size.width, center.dy), crossPaint);

    // Sweep Sector
    final sweepRect = Rect.fromCircle(center: center, radius: radius);
    final sweepPaint = Paint()
      ..shader = SweepGradient(
        startAngle: 0.0,
        endAngle: math.pi * 0.5,
        colors: [color.withAlpha(0), color.withAlpha(120)],
        transform: GradientRotation(angle - math.pi * 0.5),
      ).createShader(sweepRect)
      ..style = PaintingStyle.fill;

    canvas.drawCircle(center, radius, sweepPaint);

    // Leading Line
    final linePaint = Paint()
      ..color = color.withAlpha(220)
      ..strokeWidth = 1.5
      ..strokeCap = StrokeCap.round;

    final targetX = center.dx + radius * math.cos(angle);
    final targetY = center.dy + radius * math.sin(angle);
    canvas.drawLine(center, Offset(targetX, targetY), linePaint);

    // Center Core
    final corePaint = Paint()..color = color;
    canvas.drawCircle(center, 2.5, corePaint);
  }

  @override
  bool shouldRepaint(covariant _RadarPainter oldDelegate) {
    return oldDelegate.angle != angle || oldDelegate.color != color;
  }
}

// ============================================================================
// 7. GLASS CARD CONTAINER
// High-end translucent container with specular highlights
// ============================================================================
class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double borderRadius;
  final Color? borderColor;
  final Color? backgroundColor;

  const GlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(14),
    this.margin,
    this.borderRadius = 12.0,
    this.borderColor,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = AppColors.isDark(context);
    final bg = backgroundColor ?? (isDark ? const Color(0xFF101728) : Colors.white);
    final border = borderColor ?? (isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0));

    return Container(
      margin: margin,
      padding: padding,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(color: border, width: 0.8),
        boxShadow: [
          BoxShadow(
            color: isDark ? Colors.black.withAlpha(60) : Colors.black.withAlpha(8),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: child,
    );
  }
}
