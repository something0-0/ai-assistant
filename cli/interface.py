"""Interactive CLI with Rich."""
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


class CLI:
    def __init__(self, ai):
        self.ai = ai
        self.console = Console()

    def run(self):
        self.console.print(Panel.fit(
            f"[bold cyan]{self.ai.personality.name}[/bold cyan]\n"
            f"[dim]{self.ai.personality.data['description']}[/dim]",
            border_style="cyan"
        ))
        self.console.print(f"[green]{self.ai.personality.greeting}[/green]\n")

        while True:
            try:
                user_input = Prompt.ask("[bold blue]You[/bold blue]")
            except (KeyboardInterrupt, EOFError):
                self.console.print(f"\n[cyan]{self.ai.personality.farewell}[/cyan]")
                break

            cmd = user_input.strip()
            if not cmd:
                continue
            if cmd.startswith("/"):
                if self._handle_command(cmd):
                    break
                continue

            self.console.print("[bold green]Assistant[/bold green]:", end=" ")
            try:
                reply = self.ai.ask(cmd)
                self.console.print(reply)
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
            self.console.print()

    def _handle_command(self, cmd):
        parts = cmd.split(maxsplit=1)
        op = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if op in ("/quit", "/exit", "/q"):
            self.console.print(f"[cyan]{self.ai.personality.farewell}[/cyan]")
            return True
        elif op == "/clear":
            self.ai.clear_memory("all")
            self.console.print("[yellow]Memory cleared.[/yellow]")
        elif op == "/status":
            s = self.ai.status()
            self.console.print(Panel(
                f"Name: {s['name']}\nLLM: {s['llm_provider']}\n"
                f"Short-term: {s['short_term_messages']} msgs\n"
                f"Long-term: {s['long_term_memories']} memories",
                title="Status", border_style="magenta"
            ))
        elif op == "/remember" and arg:
            self.ai.remember(arg)
            self.console.print(f"[green]Remembered: {arg}[/green]")
        elif op == "/recall" and arg:
            mems = self.ai.recall(arg)
            if mems:
                self.console.print(Panel("\n".join(f". {m}" for m in mems),
                                         title="Recalled", border_style="yellow"))
            else:
                self.console.print("[dim]No matching memories.[/dim]")
        return False
