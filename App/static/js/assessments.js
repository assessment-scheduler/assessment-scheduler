$(document).ready(function(){
    console.log(assessments);
})

const cardContainer = document.getElementById('card_container');

assessments.forEach(assessment => {
    // Create the card element
    const card = document.createElement('div');
    card.classList.add('card');
    card.setAttribute('data-course-code', assessment.courseCode);
    
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
    courseCode.textContent = assessment.courseCode;

    const courseAssessmentLabel = document.createElement('p');
    courseAssessmentLabel.classList.add('card-label');
    courseAssessmentLabel.textContent = 'Assessment Type';
    const assessmentType = document.createElement('p');
    assessmentType.classList.add('assessment-type');
    assessmentType.textContent = assessment.a_ID;

    const caNumLabel = document.createElement('p');
    caNumLabel.classList.add('card-label');
    caNumLabel.textContent = 'Course Assessment ID';
    const caNum = document.createElement('p');
    caNum.classList.add('assessment-id');
    caNum.textContent = assessment.id

    const startDateLabel = document.createElement('p');
    startDateLabel.classList.add('card-label');
    startDateLabel.textContent = 'Start Date';
    const startDate = document.createElement('p');
    startDate.classList.add('start-date');
    startDate.textContent = assessment.startDate;

    const endDateLabel = document.createElement('p');
    endDateLabel.classList.add('card-label');
    endDateLabel.textContent = 'End Date';
    const endDate = document.createElement('p');
    endDate.classList.add('end-date');
    endDate.textContent = assessment.endDate;
    
    const startTimeLabel = document.createElement('p');
    startTimeLabel.classList.add('card-label');
    startTimeLabel.textContent = 'Start Time';
    const startTime = document.createElement('p');
    startTime.classList.add('start-time');
    startTime.textContent = assessment.startTime;

    const endTimeLabel = document.createElement('p');
    endTimeLabel.classList.add('card-label');
    endTimeLabel.textContent = 'End Time';
    const endTime = document.createElement('p');
    endDate.classList.add('end-time');
    endTime.textContent = assessment.endTime;
    
    const clashDetectedLabel = document.createElement('p');
    clashDetectedLabel.classList.add('card-label');
    clashDetectedLabel.textContent = 'Clash Detected';
    const clashDetected = document.createElement('p');
    clashDetected.classList.add('clash-detected');
    clashDetected.textContent = `${assessment.clashDetected}`;


    // Create action links (modify and delete can be replaced with actual functionality)
    const modifyLink = document.createElement('button');
    modifyLink.textContent = 'Modify';
    modifyLink.addEventListener('click', function() {
        window.location.href = `/modifyAssessment/${assessment.id}`;
    });
    const deleteLink = document.createElement('button');
    deleteLink.textContent = 'Delete';
    deleteLink.classList.add('delete_btn')
    deleteLink.addEventListener('click', function() {
        window.location.href = `/deleteAssessment/${assessment.id}`;
    });
 

    // Append elements to their respective parents
    courseDetails.appendChild(courseCodeLabel);
    courseDetails.appendChild(courseCode);
    assessmentInfo.appendChild(courseAssessmentLabel);
    assessmentInfo.appendChild(assessmentType);
    // assessmentInfo.appendChild(caNumLabel);
    // assessmentInfo.appendChild(caNum);
    assessmentInfo.appendChild(startDateLabel);
    assessmentInfo.appendChild(startDate);
    assessmentInfo.appendChild(endDateLabel);
    assessmentInfo.appendChild(endDate);
    assessmentInfo.appendChild(startTimeLabel);
    assessmentInfo.appendChild(startTime);
    assessmentInfo.appendChild(endTimeLabel);
    assessmentInfo.appendChild(endTime);
    assessmentInfo.appendChild(clashDetectedLabel);
    assessmentInfo.appendChild(clashDetected);
    actions.appendChild(modifyLink);
    actions.appendChild(deleteLink);
    card.appendChild(courseDetails);
    card.appendChild(assessmentInfo);
    card.appendChild(actions);
    
    // Append the card to the card container
    cardContainer.appendChild(card);
});