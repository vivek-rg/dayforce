import { api } from "../../shared/api";
import { useResource } from "../../shared/hooks";
import { DataState, EmptyState, PageHeader, Section } from "../../shared/ui";
import { ProposalCard } from "./ProposalCard";

export function ReviewInboxPage() {
  const inbox = useResource("review-inbox", (signal) =>
    api.reviewInbox(signal),
  );
  return (
    <>
      <PageHeader
        title="Review inbox"
        description="You approve this exact payload, against these exact versions. If anything has changed, the server refuses and asks for a fresh review."
      />
      <DataState
        resource={inbox}
        isEmpty={(data) => data.items.length === 0}
        empty="No proposals are waiting for your role."
      >
        {(data) => {
          const waiting = data.items.filter((item) => !item.decision);
          const decided = data.items.filter((item) => item.decision);
          return (
            <>
              <Section title={`Awaiting decision (${waiting.length})`}>
                {waiting.length ? (
                  <div className="stack">
                    {waiting.map((proposal) => (
                      <ProposalCard
                        key={proposal.id}
                        proposal={proposal}
                        onChanged={inbox.reload}
                      />
                    ))}
                  </div>
                ) : (
                  <EmptyState>Nothing is waiting for a decision.</EmptyState>
                )}
              </Section>
              {decided.length > 0 && (
                <Section title={`Decided (${decided.length})`}>
                  <div className="stack">
                    {decided.map((proposal) => (
                      <ProposalCard
                        key={proposal.id}
                        proposal={proposal}
                        onChanged={inbox.reload}
                      />
                    ))}
                  </div>
                </Section>
              )}
            </>
          );
        }}
      </DataState>
    </>
  );
}
