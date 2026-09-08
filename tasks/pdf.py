from django.template.loader import render_to_string


def render_task_pdf(task) -> bytes:
    """Rend la fiche PDF d'une tâche via WeasyPrint (import tardif : dépend de
    libs système pango/cairo)."""
    from weasyprint import HTML

    html = render_to_string("tasks/task_sheet.html", {"task": task})
    return HTML(string=html, base_url=".").write_pdf()
