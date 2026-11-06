import { api, downloadDocument } from "../../shared/api";
import {
  documentCategoryLabel,
  documentTone,
  formatBytes,
  formatDateTime,
  humanize,
} from "../../shared/format";
import { useAction, useResource } from "../../shared/hooks";
import { latestReviewReason } from "../../shared/logic";
import { ActionError, Badge, DataState, DataTable } from "../../shared/ui";

export function DocumentsTab({ hireId }: { hireId: string }) {
  const documents = useResource(`documents:${hireId}`, (signal) =>
    api.hireDocuments(hireId, signal),
  );
  const download = useAction();
  return (
    <DataState
      resource={documents}
      isEmpty={(data) => data.items.length === 0}
      empty="No documents have been submitted."
    >
      {(data) => (
        <>
          <ActionError error={download.error} />
          <DataTable
            caption="Documents"
            rowKey={(item) => item.id}
            rows={data.items}
            minWidth={760}
            columns={[
              {
                header: "Category",
                render: (item) => documentCategoryLabel(item.category),
              },
              {
                header: "State",
                render: (item) => (
                  <>
                    <Badge tone={documentTone(item.state)}>
                      {humanize(item.state)}
                    </Badge>
                    {latestReviewReason(item) && (
                      <span className="cell-sub">
                        {latestReviewReason(item)}
                      </span>
                    )}
                  </>
                ),
              },
              { header: "File", render: (item) => item.original_name },
              {
                header: "Size",
                numeric: true,
                render: (item) => (
                  <span className="num">{formatBytes(item.size_bytes)}</span>
                ),
              },
              {
                header: "Submitted",
                render: (item) => (
                  <span className="num">{formatDateTime(item.created_at)}</span>
                ),
              },
              {
                header: "",
                render: (item) => (
                  <button
                    type="button"
                    className="btn btn-sm"
                    aria-label={`Download ${item.original_name}`}
                    disabled={download.pending}
                    onClick={() =>
                      void download.run(() =>
                        downloadDocument(item.id, item.original_name),
                      )
                    }
                  >
                    Download
                  </button>
                ),
              },
            ]}
          />
        </>
      )}
    </DataState>
  );
}
