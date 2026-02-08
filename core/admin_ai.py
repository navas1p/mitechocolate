from django.template.response import TemplateResponse

from .ai import ask_ai
from .forms import AdminAssistantForm
from .models import AssistantMessage
import os


def assistant_view(request):
    answer = None
    error = None
    if request.method == "POST":
        form = AdminAssistantForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data["question"]
            answer = ask_ai(question)
            AssistantMessage.objects.create(
                question=question,
                answer=answer,
                asked_by=getattr(request.user, "username", ""),
                source="assistant",
            )
        else:
            error = "Please enter a question."
    else:
        form = AdminAssistantForm()

    context = {
        **request.admin_site.each_context(request),
        "form": form,
        "answer": answer,
        "error": error,
        "has_api_key": bool(os.environ.get("OPENAI_API_KEY")),
        "title": "AI Assistant",
    }
    return TemplateResponse(request, "admin/assistant.html", context)
