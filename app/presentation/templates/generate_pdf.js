window.jsPDF = window.jspdf.jsPDF;

const font_size_normal = 10;
const font_size_title = 16;
const margin_left = 20;
const table_width = 170
const line_height = 7;

const generate_pdf = (data) => {
    const doc = new jsPDF();
    doc.y = line_height;
    doc.page_number = 1;
    empty_line(doc, 3);
    section_header(doc, "Zorgfiche - Intake");
    empty_line(doc, 2);

    section_header(doc, "Administratieve gegevens", true);
    empty_line(doc, 2);

    topic_header(doc,"Leerling:");

    topic(doc, [{header: "Naam: ", text: data.s_last_name}, {header: "Voornaam: ", text: data.s_first_name}]);
    topic(doc, [{header: "Geboortedatum : ", text: data.s_date_of_birth ? data.s_date_of_birth : ''},
        {header: "Geslacht: ", text: data.s_sex}, {header: "Code: ", text: data.s_code}]);

    topic_header(doc, "Intaker:");
    topic(doc, [{header: "Naam: ", text: data.i_last_name}, {header: "Voornaam: ", text: data.i_first_name}]);
    topic(doc, [{header: "Intakedatum : ", text: data.i_intake_date ? data.i_intake_date : ''},
        {header: "Code: ", text: data.i_code}]);

    topic_header(doc, "Contactgegevens:");
    topic(doc,{header: 'Vorige school: ', text: data.vorige_school}, 2, true);
    topic(doc,{header: 'Vorig CLB: ', text: data.vorig_clb}, 2, true);

    empty_line(doc);
    topic_header(doc, "Inschrijving:");
    topic_bool(doc, "Met gemotiveerd verslag", data.f_gemotiveerd_verslag);
    topic_bool(doc, "Met verslag onder ontbindende voorwaarden", data.f_verslag_ontbindende_voorwaarden);
    topic_bool(doc, "Zonder verslag én met specifieke onderwijsbehoefte", data.f_verslag_ontbindende_voorwaarden);

    empty_line(doc);
    topic_header(doc, "Nood aan voorspelbaarheid:");
    topic_bool(doc, "Uitnodigen startmoment augustus", data.f_nood_aan_voorspelbaarheid);

    footer(doc, `${data.s_last_name}-${data.s_first_name}.pdf`);

    empty_line(doc);
    section_header(doc, "Beeld over de leerling", true);
    empty_line(doc);
    topic_header(doc, "Thuissituatie:")
    topic(doc, {header: '', text: data.thuissituatie}, 5, true)

    empty_line(doc);
    topic_header(doc, "Schoolverloop:")
    topic(doc, {header: 'Schoolloopbaan/studietraject: ', text: data.schoolloopbaan}, 4, true)
    topic(doc, {header: 'Advies lagere school: ', text: data.advies_school}, 2, true)
    topic(doc, {header: 'Definitieve studiekeuze leerling: ', text: data.definitieve_studiekeuze}, 2, true)

    empty_line(doc);
    topic_header(doc, "(Psycho-)medische info en verstandelijke mogelijkheden:")
    topic_bool(doc, "ASS", data.f_ass, data.ass);
    topic_bool(doc, "ADD", data.f_add, data.add);
    topic_bool(doc, "ADHD", data.f_adhd, data.adhd);
    topic_bool(doc, "DCD", data.f_dcd, data.dcd);
    topic_bool(doc, "Hoogbegaafd", data.f_hoogbegaafd, data.hoogbegaafd);
    topic_bool(doc, "Dyscalculie", data.f_dyscalculie, data.dyscalculie);
    topic_bool(doc, "Dyslexie", data.f_dyslexie, data.dyslexie);
    topic_bool(doc, "Dysorthografie", data.f_dysorthografie, data.dysorthografie);
    topic_bool(doc, "Stos/dysfasie", data.f_stos_dysfasie, data.stos_dysfasie);
    topic_bool(doc, "Andere", data.f_andere, data.andere);
    topic(doc, {header: 'motoriek (fijne, grove, evenwicht, combinatie, nauwkeurigheid): ', text: data.motoriek}, 4, true);
    topic(doc, {header: 'gezondheid (astma, epilepsie, diabetes, allergie, ziekte, medicatie): ', text: data.gezondheid}, 4, true);

    footer(doc, `${data.s_last_name}-${data.s_first_name}.pdf`);

    empty_line(doc);
    topic_header(doc, "Sociaal-emotioneel functioneren:");
    topic(doc, {header: 'Groepsfunctioneren (assertiviteit, probleemoplossend, conflicthanterend, leerling-leerling, leerling-leerkracht):             ', text: data.groepsfunctioneren}, 10, true);
    topic(doc, {header: 'Individueel functioneren (faalangst, signalen stemming, vermogen tot zelfreflectie, herkennen van gevoelens, behoefte aan voorspelbaarheid, prikkelgevoeligheid, motivatie, zelfredzaamheid): ', text: data.individueel_functioneren}, 10, true);
    topic(doc, {header: 'Communicatie (begrijpen van opdrachten, vragen durven stellen, letterlijk nemen van comunnicatie):                 ', text: data.communicatie}, 10, true);

    footer(doc, `${data.s_last_name}-${data.s_first_name}.pdf`);

    empty_line(doc);
    topic_header(doc, "Leerontwikkeling:");
    topic(doc, {header: 'Algemeen (aandacht, orde, organisatie, werktempo): ', text: data.algemeen}, 10, true);
    topic(doc, {header: 'Taalvaardigheid: ', text: data.taalvaardigheid}, 10, true);
    topic(doc, {header: 'Rekenvaardigheid: ', text: data.rekenvaardigheid}, 10, true);

    footer(doc, `${data.s_last_name}-${data.s_first_name}.pdf`);

    empty_line(doc);
    section_header(doc, "Ondersteuning / tips in aanpak", true);
    empty_line(doc);
    topic_header(doc, "Ondersteunende maatregelen:");
    topic(doc, {header: '', text: data.ondersteunende_maatregelen}, 20, true);
    empty_line(doc);
    topic_header(doc, 'Schoolexterne zorg (logopedist, kinesist, huiswerkbegeleider,');
    topic_header(doc, 'psychiater, auti-coach, thuisbegeleiding, jeugdconsulent):');
    topic(doc, {header: '', text: data.ondersteunende_maatregelen}, 10, true);

    footer(doc, `${data.s_last_name}-${data.s_first_name}.pdf`, false);

    // console.log('style', doc.getFont());
    // console.log('fontsize', doc.getFontSize());
    // console.log('stylelist', doc.getFontList());

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

