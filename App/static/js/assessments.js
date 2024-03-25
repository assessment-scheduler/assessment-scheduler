a1={
    code:'COMP1601',
    type:'Assignment',
    duration:'120',
    details:'',
    weight:'15'
}

a2={
    code:'COMP1601',
    type:'Exam',
    duration:'120',
    details:'Written exam - FST113',
    weight:'25'
}

a3={
    code:'COMP1603',
    type:'Presentation',
    duration:'120',
    details:'DCIT Conference room',
    weight:'12'
}


assessments=[a1,a2,a3]
const cardContainer = document.getElementById('card_container');

assessments.forEach(assessment => {
    // Create the card element
    const card = document.createElement('div');
    card.classList.add('card');
    card.setAttribute('data-course-code', assessment.code);
    
    // Create elements for course details, assessment info, and actions
    const courseDetails = document.createElement('div');
    courseDetails.classList.add('course-details');
    const assessmentInfo = document.createElement('div');
    assessmentInfo.classList.add('assessment-info');
    const actions = document.createElement('div');
    actions.classList.add('actions');

    // Create content for course details
    const courseCodeLabel = document.createElement('p');
    courseCodeLabel.classList.add('card-label');
    courseCodeLabel.textContent = 'Course Code';
    const courseCode = document.createElement('p');
    courseCode.classList.add('course-code');
    courseCode.textContent = assessment.code;

    const courseAssessmentLabel = document.createElement('p');
    courseAssessmentLabel.classList.add('card-label');
    courseAssessmentLabel.textContent = 'Assessment Type';
    const assessmentType = document.createElement('p');
    assessmentType.classList.add('assessment-type');
    assessmentType.textContent = assessment.type;

    const durationLabel = document.createElement('p');
    durationLabel.classList.add('card-label');
    durationLabel.textContent = 'Duration';
    const duration = document.createElement('p');
    duration.classList.add('duration');
    duration.textContent = assessment.duration+" mins";

    const detailsLabel = document.createElement('p');
    detailsLabel.classList.add('card-label');
    detailsLabel.textContent = 'Details';
    const details = document.createElement('p');
    details.classList.add('details');
    details.textContent = assessment.details;

    const weightLabel = document.createElement('p');
    weightLabel.classList.add('card-label');
    weightLabel.textContent = 'Weight';
    const weight = document.createElement('p');
    weight.classList.add('weight');
    weight.textContent = assessment.weight+"%";

    // Create action links (modify and delete can be replaced with actual functionality)
    const modifyLink = document.createElement('button');
    modifyLink.textContent = 'Modify';
    modifyLink.addEventListener('click', function() {
        window.location.href = `/modifyAssessment/${assessment.code}`;
    });
    const deleteLink = document.createElement('button');
    deleteLink.textContent = 'Delete';
    deleteLink.classList.add('delete_btn')
    deleteLink.href = '#'; // Replace with actual delete functionality

    // Append elements to their respective parents
    courseDetails.appendChild(courseCodeLabel);
    courseDetails.appendChild(courseCode);
    assessmentInfo.appendChild(courseAssessmentLabel);
    assessmentInfo.appendChild(assessmentType);
    courseDetails.appendChild(durationLabel);
    courseDetails.appendChild(duration);
    assessmentInfo.appendChild(weightLabel);
    assessmentInfo.appendChild(weight);
    courseDetails.appendChild(detailsLabel);
    courseDetails.appendChild(details);
    actions.appendChild(modifyLink);
    actions.appendChild(deleteLink);
    card.appendChild(courseDetails);
    card.appendChild(assessmentInfo);
    card.appendChild(actions);

    // Append the card to the card container
    cardContainer.appendChild(card);
});