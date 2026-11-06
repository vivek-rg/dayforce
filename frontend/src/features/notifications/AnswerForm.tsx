import { useState } from "react";
import { api } from "../../shared/api";
import { useAction } from "../../shared/hooks";
import { ActionError, Field } from "../../shared/ui";

export function AnswerForm({
  questionId,
  onAnswered,
}: {
  questionId: string;
  onAnswered: () => void;
}) {
  const [answer, setAnswer] = useState("");
  const action = useAction();

  async function submit() {
    const result = await action.run(() =>
      api.answerQuestion(questionId, answer.trim()),
    );
    if (result.ok) {
      setAnswer("");
      onAnswered();
    }
  }

  return (
    <div className="answer-form">
      <Field
        label="Your answer"
        hint="An answer is information. It is not an approval."
      >
        <textarea
          className="input"
          rows={2}
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
        />
      </Field>
      <ActionError error={action.error} onReload={onAnswered} />
      <button
        type="button"
        className="btn btn-sm btn-primary"
        disabled={!answer.trim() || action.pending}
        onClick={() => void submit()}
      >
        {action.pending ? "Sending" : "Send answer"}
      </button>
    </div>
  );
}
