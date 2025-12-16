from fpdf import FPDF

def generate_report(results, filename="verification_report.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    pdf.cell(0, 10, "Research Verification Report", ln=True)

    for r in results:
        pdf.multi_cell(0, 8, f"\nClaim:\n{r['claim']}")
        if r["verified"]:
            for m in r["matches"]:
                pdf.multi_cell(
                    0, 6,
                    f"- {m['pdf']} | Page {m['page']} | Score {m['score']}"
                )
        else:
            pdf.multi_cell(0, 6, "Not verified")

    pdf.output(filename)
    return filename
