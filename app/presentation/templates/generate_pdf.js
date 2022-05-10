window.jsPDF = window.jspdf.jsPDF;

const font_size_normal = 10;
const font_size_title = 16;
const margin_left = 20;
const table_width = 170
const line_height = 7;

const generate_pdf = (template, data) => {
    const doc = new jsPDF();
    doc.y = line_height;
    doc.page_number = 1;

    template.forEach(item => {
        new Function('doc', 'data', item)(doc, data);
    });

    doc.save(`${data.s_last_name}-${data.s_first_name}.pdf`);
}

const empty_line = (doc, nbr = 1) => {
    doc.y += nbr * line_height
};

const section_header = (doc, text, inverse=false) => {
    doc.setFontSize(font_size_title);
    if (inverse) {
        doc.rect(margin_left, doc.y - line_height + 2, table_width, line_height, 'F');
        doc.setTextColor(255);
        doc.text(text, margin_left + table_width/2, doc.y, {align: 'center'})
        doc.setTextColor(0);
    } else {
        doc.text(text, margin_left + table_width/2, doc.y, {align: 'center'})

    }
    doc.y += line_height;
    doc.setFontSize(font_size_normal);

}

const topic_header = (doc, text) => {
    doc.setFontSize(font_size_title);
    doc.setFont("helvetica", "bold");
    doc.text(text, margin_left, doc.y)
    doc.setFontSize(font_size_normal);
    doc.setFont("helvetica", "normal");
    doc.y += line_height;
}


const topic = (doc, data, nbr_lines=1, fill_cell=false) => {
    let x = 2 + margin_left;
    if (Array.isArray(data)) {
        const x_offset = (table_width - 2) / data.length;
        doc.rect(margin_left, doc.y - line_height + 2, table_width, line_height);
        data.forEach(item => {
            bold_and_normal(doc, item.header, item.text, x, doc.y)
            x += x_offset;
        });
    } else {
        doc.rect(margin_left, doc.y - line_height + 2, table_width, line_height * nbr_lines);
        bold_and_normal(doc, data.header, data.text, x, doc.y, fill_cell ? table_width - 5 : 0);
    }
    doc.y += line_height * nbr_lines
}

const topic_bool = (doc, header, flag, text = null) => {
    doc.rect(margin_left, doc.y - line_height + 2, 10, line_height);
    doc.rect(margin_left + 10, doc.y - line_height + 2, table_width - 10, line_height);
    doc.setFontSize(font_size_title);
    doc.setFont("helvetica", "bold");
    doc.text(flag ? 'X' : '', margin_left + 3, doc.y)
    doc.setFontSize(font_size_normal);
    doc.setFont("helvetica", "normal");
    bold_and_normal(doc, header, flag && (text || text === '') ? `: ${text}` : '', margin_left + 12, doc.y);
    doc.y += line_height;
}

const footer = (doc, text, new_page=true) => {
    doc.text(`${text}         ${doc.page_number}`, 110, 290, {align: 'center'});
    doc.page_number += 1;
    if (new_page) {
        doc.addPage();
        doc.y = line_height;
    }
}

const bold_and_normal = (doc, heading, text, x, y, max_width=0) => {
    doc.setFontSize(font_size_normal);
    doc.setFont("helvetica", "bolditalic");
    const heading_width = doc.getStringUnitWidth(heading) * font_size_normal * 25.6 / 72;
    doc.text(heading, x, y, {'maxWidth': max_width})
    doc.setFont("helvetica", "normal");
    doc.text( `${' '.repeat(heading_width * 1.05)}${text}`, x, y, {'maxWidth': max_width})
}

