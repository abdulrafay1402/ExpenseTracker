import 'package:flutter/material.dart';

/// Reusable error state widget (perfective maintenance).
///
/// Replaces the same "icon + message + retry button" block that was
/// copy-pasted across list screens, so a design change only needs
/// to happen in one place.
class ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;

  const ErrorView({
    super.key,
    this.message = 'Something went wrong',
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.cloud_off, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 12),
            Text(message, style: TextStyle(color: Colors.grey[600])),
            const SizedBox(height: 12),
            if (onRetry != null)
              FilledButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
          ],
        ),
      ),
    );
  }
}
