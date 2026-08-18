import 'package:flutter/material.dart';

class PageFrame extends StatelessWidget {
  final String title;
  final String? subtitle;
  final List<Widget> actions;
  final Widget child;
  const PageFrame({super.key, required this.title, this.subtitle, this.actions = const [], required this.child});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          LayoutBuilder(
            builder: (context, constraints) {
              final isCompact = constraints.maxWidth < 760;
              final titleBlock = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  if (subtitle != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(
                        subtitle!,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(color: Color(0xFF6B6B6B)),
                      ),
                    ),
                ],
              );

              final maxActionWidth = isCompact
                  ? constraints.maxWidth
                  : (constraints.maxWidth < 360 ? constraints.maxWidth : 360.0);
              final actionsBlock = actions.isEmpty
                  ? const SizedBox.shrink()
                  : Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      alignment: isCompact ? WrapAlignment.start : WrapAlignment.end,
                      children: actions
                          .map(
                            (action) => ConstrainedBox(
                              constraints: BoxConstraints(maxWidth: maxActionWidth),
                              child: action,
                            ),
                          )
                          .toList(),
                    );

              if (isCompact) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    titleBlock,
                    if (actions.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      actionsBlock,
                    ],
                  ],
                );
              }

              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: titleBlock),
                  const SizedBox(width: 16),
                  Flexible(child: actionsBlock),
                ],
              );
            },
          ),
          const SizedBox(height: 16),
          Expanded(child: child),
        ],
      ),
    );
  }
}

class LoadingView extends StatelessWidget {
  const LoadingView({super.key});

  @override
  Widget build(BuildContext context) => const Center(child: CircularProgressIndicator());
}

class ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;
  const ErrorView(this.message, {super.key, this.onRetry});

  @override
  Widget build(BuildContext context) => Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.error_outline, size: 40),
                  const SizedBox(height: 12),
                  Text(message, textAlign: TextAlign.center),
                  if (onRetry != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
                    ),
                ],
              ),
            ),
          ),
        ),
      );
}

class EmptyView extends StatelessWidget {
  final String text;
  final Widget? action;
  const EmptyView(this.text, {super.key, this.action});

  @override
  Widget build(BuildContext context) => Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 620),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(text, textAlign: TextAlign.center),
                  if (action != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: action!,
                    ),
                ],
              ),
            ),
          ),
        ),
      );
}

class ErrorBanner extends StatelessWidget {
  final String message;
  final EdgeInsetsGeometry margin;
  const ErrorBanner(this.message, {super.key, this.margin = const EdgeInsets.only(bottom: 12)});

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        margin: margin,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFFFFF3F0),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE6C5BE)),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.error_outline, size: 20, color: Color(0xFF8A2D22)),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                message,
                softWrap: true,
                style: const TextStyle(color: Color(0xFF8A2D22), height: 1.35),
              ),
            ),
          ],
        ),
      );
}

class LabeledText extends StatelessWidget {
  final String label;
  final String? value;
  const LabeledText(this.label, this.value, {super.key});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(color: Color(0xFF6B6B6B), fontSize: 12)),
            SelectableText(
              (value == null || value!.isEmpty) ? '—' : value!,
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
            ),
          ],
        ),
      );
}


class SummaryStatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final double width;
  const SummaryStatCard({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    this.width = 260,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      child: Card(
        clipBehavior: Clip.antiAlias,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, size: 26),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: FittedBox(
                  fit: BoxFit.scaleDown,
                  alignment: Alignment.centerLeft,
                  child: Text(
                    value,
                    maxLines: 1,
                    style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w900, height: 1.05),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                title,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(height: 1.2),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

double responsiveCardWidth(double maxWidth, {double min = 220, double max = 290, double gap = 12}) {
  final safeWidth = maxWidth.isFinite && maxWidth > 0 ? maxWidth : max;
  var columns = 1;
  if (safeWidth >= 1160) {
    columns = 4;
  } else if (safeWidth >= 860) {
    columns = 3;
  } else if (safeWidth >= 580) {
    columns = 2;
  }
  final width = (safeWidth - gap * (columns - 1)) / columns;
  if (width < min) return safeWidth < min ? safeWidth : min;
  if (width > max) return max;
  return width;
}

class AppActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onPressed;
  final bool filled;
  final double width;

  const AppActionButton({
    super.key,
    required this.icon,
    required this.label,
    required this.onPressed,
    this.filled = false,
    this.width = 260,
  });

  @override
  Widget build(BuildContext context) {
    final child = SizedBox(
      width: width,
      child: Text(
        label,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        textAlign: TextAlign.center,
      ),
    );

    final style = filled
        ? FilledButton.styleFrom(minimumSize: const Size(0, 56), padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12))
        : OutlinedButton.styleFrom(minimumSize: const Size(0, 56), padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12));

    if (filled) {
      return FilledButton.icon(onPressed: onPressed, icon: Icon(icon), label: child, style: style);
    }
    return OutlinedButton.icon(onPressed: onPressed, icon: Icon(icon), label: child, style: style);
  }
}
