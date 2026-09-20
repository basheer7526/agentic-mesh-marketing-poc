"""
Notification service abstraction.

Provides a Protocol-based interface so that future
notification backends (Email, Slack, Teams) can be
added without changing the graph or workflow service.

Current implementation: ConsoleNotificationService
(prints a structured digest summary to stdout).
"""

from typing import Protocol, runtime_checkable

from app.models.digest import DailyDigest, Priority


@runtime_checkable
class NotificationService(Protocol):
    """
    Interface for all notification backends.

    Implementations must accept a DailyDigest and
    deliver it through their respective channel.
    """

    def send(self, digest: DailyDigest) -> None:
        ...


class ConsoleNotificationService:
    """
    Development notification backend.

    Prints a concise digest summary to stdout.
    Satisfies the NotificationService Protocol.
    """

    def send(self, digest: DailyDigest) -> None:
        """
        Print a formatted digest summary to the console.
        """

        print("\n" + "=" * 60)
        print("  MARKETING INTELLIGENCE DIGEST")
        print("=" * 60)
        print(f"  Date            : {digest.date}")
        print(f"  Total articles  : {digest.total_articles}")
        print(f"  High priority   : {digest.high_priority}")
        print(f"  Medium priority : {digest.medium_priority}")
        print(f"  Low priority    : {digest.low_priority}")
        print("=" * 60)

        for index, item in enumerate(
            digest.items,
            start=1,
        ):

            priority_label = item.priority.value

            print(
                f"\n[{index}] [{priority_label}] "
                f"{item.headline}"
            )
            print(f"    Source: {item.source}")
            print(f"    {item.summary}")

        print("\n" + "=" * 60)
        print("  END OF DIGEST")
        print("=" * 60 + "\n")


# Shared instance used by the notification node.
# Swap this for a different implementation to change
# the delivery channel without touching the graph.
notification_service = ConsoleNotificationService()
