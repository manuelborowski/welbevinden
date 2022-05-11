window.jsPDF = window.jspdf.jsPDF;

const font_size_normal = 9;
const font_size_title = 16;
const margin_left = 20;
const table_width = 170
const line_height = 7;

const generate_pdf = (template, data) => {
    const doc = new jsPDF();
    doc.y = line_height;
    doc.page_number = 1;

    empty_line(doc, 2);
    section_header(doc, "Inschrijvingsformulier - schooljaar 2022-2023", true);
    empty_line(doc);

    topic_header(doc, "Intaker:");
    topic(doc, [{header: "Naam: ", text: data.i_last_name}, {header: "Voornaam: ", text: data.i_first_name}]);
    topic(doc, [{header: "Intakedatum : ", text: data.i_intake_date ? data.i_intake_date : ''}, {header: "Code: ", text: data.i_code}]);

    topic_header(doc,"Leerling:");
    topic(doc, [{header: "Naam: ", text: data.s_last_name}, {header: "Voornaam: ", text: data.s_first_name}]);
    topic(doc, [{header: "Geboortedatum : ", text: data.s_date_of_birth ? data.s_date_of_birth : ''}, {header: "Geslacht: ", text: data.s_sex}, {header: "Code: ", text: data.s_code}]);
    selectbox(doc, 'officieel adres bij: ', ['ouders', 'mama', 'papa', 'andere'], data.s_officieel_adres_bij, true);
    topic(doc, {header: "andere: ", text: data.s_officieel_adres_andere});

    empty_line(doc);
    topic_header(doc, 'Schoolloopbaan:');
    selectbox(doc, '', [' basisonderwijs', 'buitengewoon basisonderwijs', 'secundair onderwijs', 'buitengewoon secundair onderwijs'], data.school_type, true)
    topic(doc, [{header: "naam (basis)school: ", text: data.school_naam, width: 80}, {header: "BLO type: ", text: data.school_blo_type, width: 20}]);
    topic(doc, {header: "adres (basis)school: ", text: data.school_adres});
    topic(doc, {header: "(voorlopig) advies: ", text: data.school_voorlopig_advies});
    topic(doc, [{header: "schooljaar", text: "", width: 10}, {header: "school+gemeente", text: "", width: 40}, {header: "jaar/studierichting/onderwijsvorm", text: "", width: 35}, {header: "attest+clausule", text: "", width: 15} ]);
    topic(doc, [{header: "", text: data.school_lijst[0].jaar, width: 10}, {header: "", text: data.school_lijst[0].adres, width: 40}, {header: "", text: data.school_lijst[0].studierichting, width: 35}, {header: "", text: data.school_lijst[0].attest, width: 15} ]);
    topic(doc, [{header: "", text: data.school_lijst[1].jaar, width: 10}, {header: "", text: data.school_lijst[1].adres, width: 40}, {header: "", text: data.school_lijst[1].studierichting, width: 35}, {header: "", text: data.school_lijst[1].attest, width: 15} ]);
    topic(doc, [{header: "", text: data.school_lijst[2].jaar, width: 10}, {header: "", text: data.school_lijst[2].adres, width: 40}, {header: "", text: data.school_lijst[2].studierichting, width: 35}, {header: "", text: data.school_lijst[2].attest, width: 15} ]);
    topic(doc, [{header: "", text: data.school_lijst[3].jaar, width: 10}, {header: "", text: data.school_lijst[3].adres, width: 40}, {header: "", text: data.school_lijst[3].studierichting, width: 35}, {header: "", text: data.school_lijst[3].attest, width: 15} ]);
    topic(doc, [{header: "", text: data.school_lijst[4].jaar, width: 10}, {header: "", text: data.school_lijst[4].adres, width: 40}, {header: "", text: data.school_lijst[4].studierichting, width: 35}, {header: "", text: data.school_lijst[4].attest, width: 15} ]);
    topic(doc, [{header: "", text: data.school_lijst[5].jaar, width: 10}, {header: "", text: data.school_lijst[5].adres, width: 40}, {header: "", text: data.school_lijst[5].studierichting, width: 35}, {header: "", text: data.school_lijst[5].attest, width: 15} ]);





    // template.forEach(item => {
    //     new Function('doc', 'data', item)(doc, data);
    // });

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
        if('width' in data[0]) {
            data.forEach(d => d.offset = table_width * d.width / 100);
        } else {
            data.forEach(d => d.offset = table_width / data.length);
        }
        let x_offset = margin_left + 2;
        doc.rect(margin_left, doc.y - line_height + 2, table_width, line_height);
        data.forEach(item => {
            bold_and_normal(doc, item.header, item.text, x_offset, doc.y)
            x_offset += item.offset;
        });
    } else {
        doc.rect(margin_left, doc.y - line_height + 2, table_width, line_height * nbr_lines);
        bold_and_normal(doc, data.header, data.text, x, doc.y, fill_cell ? table_width - 5 : 0);
    }
    doc.y += line_height * nbr_lines
}

const checkbox = (doc, header, flag, text = null) => {
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

const selectbox = (doc, header, items, item_set, inline=false) => {
    const nbr_lines = inline ? 1 : items.length;
    const set_id = parseInt(item_set.split(':')[0]);
    doc.rect(margin_left, doc.y - line_height + 2, table_width, line_height * nbr_lines);
    if (inline) {
        let text = '';
        for (i=0; i < items.length; i++) {
            const check = (i + 1) === set_id ? '(X)' : '( )';
            text += check + ' ' + items[i] + '  ';
        }
        bold_and_normal(doc, header, text , margin_left + 3, doc.y)
    }
    doc.y += line_height * nbr_lines;
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
    let heading_width = heading !== '' ? doc.getCharWidthsArray(heading).reduce((x, y) => x + y) * 3.4 : 0;
    // const heading_width = heading !== '' ? doc.getCharWidthsArray(heading).reduce((x, y) => x + y) * 2 + heading.length * 0.2 : 0;
    if (heading_width > 0) {
        const space_width = heading.length * 0.16
        console.log(heading, heading_width, space_width, heading_width + space_width)
        heading_width += space_width;
    }
    // const heading_width = heading.length * 2;
    // const heading_width = doc.getStringUnitWidth(heading) * font_size_normal * 28 / 72;
    doc.text(heading, x, y, {'maxWidth': max_width})
    doc.setFont("helvetica", "normal");
    doc.text( `${' '.repeat(heading_width)}${text}`, x, y, {'maxWidth': max_width})
}

