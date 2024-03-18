a1={
    code:'COMP1601',
    title:'Programming 1',
    type:'Assignment',
    date:'23/10/2023-11:00 PM'
}

a2={
    code:'COMP1601',
    title:'Programming 1',
    type:'Assignment',
    date:'29/11/2023-11:00 PM'
}

a3={
    code:'COMP1603',
    title:'Programming 3',
    type:'Assignment',
    date:'03/12/2023-11:00 PM'
}

a4={
    code:'COMP1603',
    title:'Programming 3',
    type:'Exam',
    date:'18/11/2023-11:00 AM'
}

assessments=[a1,a2,a3,a4]
const cardContainer = document.getElementById('card_container');

assessments.forEach(assessment => {
    // Create the card element
    const card = document.createElement('div');
    card.classList.add('card');

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

    const courseTitleLabel = document.createElement('p');
    courseTitleLabel.classList.add('card-label');
    courseTitleLabel.textContent = 'Course Title';
    const courseName = document.createElement('p');
    courseName.classList.add('course-title');
    courseName.textContent = assessment.title;

    const courseAssessmentLabel = document.createElement('p');
    courseAssessmentLabel.classList.add('card-label');
    courseAssessmentLabel.textContent = 'Assessment Type';
    const assessmentType = document.createElement('p');
    assessmentType.classList.add('assessment-type');
    assessmentType.textContent = assessment.type;

    const dueDateLabel = document.createElement('p');
    dueDateLabel.classList.add('card-label');
    dueDateLabel.textContent = 'Due Date';
    const dueDate = document.createElement('p');
    dueDate.classList.add('due-date');
    dueDate.textContent = assessment.date;

    // Create action links (modify and delete can be replaced with actual functionality)
    const modifyLink = document.createElement('button');
    modifyLink.textContent = 'Modify';
    modifyLink.href = '#'; // Replace with actual modify functionality
    const deleteLink = document.createElement('button');
    deleteLink.textContent = 'Delete';
    deleteLink.classList.add('delete_btn')
    deleteLink.href = '#'; // Replace with actual delete functionality

    // Append elements to their respective parents
    courseDetails.appendChild(courseCodeLabel);
    courseDetails.appendChild(courseCode);
    courseDetails.appendChild(courseTitleLabel);
    courseDetails.appendChild(courseName);
    assessmentInfo.appendChild(courseAssessmentLabel);
    assessmentInfo.appendChild(assessmentType);
    assessmentInfo.appendChild(dueDateLabel);
    assessmentInfo.appendChild(dueDate);
    actions.appendChild(modifyLink);
    actions.appendChild(deleteLink);
    card.appendChild(courseDetails);
    card.appendChild(assessmentInfo);
    card.appendChild(actions);

    // Append the card to the card container
    cardContainer.appendChild(card);
});