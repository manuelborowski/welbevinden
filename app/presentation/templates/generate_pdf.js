window.jsPDF = window.jspdf.jsPDF;


const generate_pdf = (data) => {
    console.log(data)
    const doc = new jsPDF();
    doc.text("Zorgfiche - Intake", 80, 30,{align: 'center'});

    doc.rect(25, 49, 160, 8, 'F');
    doc.setTextColor(255);
    doc.text("Administratieve gegevens", 105, 55, {align: 'center'})
    doc.setTextColor(0);

    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("Leerling:", 25, 68)
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.rect(25, 70, 160, 7);
    doc.text(`Naam: ${data.s_last_name}`, 27, 75);
    doc.text(`Voornaam: ${data.s_first_name}`, 95, 75);
    doc.rect(25, 77, 160, 7);
    doc.text(`Geboortedatum: ${data.s_date_of_birth ? data.s_date_of_birth : ''}`, 27, 82);
    doc.text(`Geslacht: ${data.s_sex}`,95, 82);
    doc.text(`Code: ${data.s_code}`,140, 82);

    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("Intaker:", 25, 91);
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.rect(25, 93, 160, 7);
    doc.text(`Naam: ${data.i_last_name}`, 27, 98);
    doc.text(`Voornaam: ${data.i_first_name}`, 95, 98);
    doc.rect(25, 100, 160, 7);
    doc.text(`Intakedatum: ${data.i_intake_date ? data.i_intake_date : ''}`, 27, 105);
    doc.text(`Code: ${data.i_code}`,95, 105);


    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("Contactgegevens:", 25, 114);
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.rect(25, 116, 160, 35);
    doc.text(`Vorige school: ${data.vorige_school}`, 27, 121, {'maxWidth': 150});
    doc.setFont("helvetica", "bold");
    doc.text(`Vorige school:`, 27, 121);
    doc.setFont("helvetica", "normal");
    doc.text(`Vorig CLB: ${data.vorig_clb}`, 27, 137, {'maxWidth': 150});


    console.log('style', doc.getFont());
    console.log('fontsize', doc.getFontSize());
    console.log('stylelist', doc.getFontList());


    doc.save(`${data.s_last_name}-${data.s_first_name}.pdf`);

}