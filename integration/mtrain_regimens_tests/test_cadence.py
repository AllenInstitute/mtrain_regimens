import pytest


def test_progression_result(
    session_fixture,
    mouse_fixture,
    progression_fixture,
):
    mouse, training_history = progression_fixture

    for session in progression_fixture['sessions']:
        response = session_fixture.post(
            'http://localhost:5000/set_training/{}' \
                .format(mouse_fixture['id']),
            data=session,
        )

        if response.status_code != 200:
            response.raise_for_status()
    
    response = session_fixture.get(
        'http://localhost:5000/state/{}' \
            .format(mouse.id),
    )

    if response.status_code != 200:
        response.raise_for_status()
    
    assert response.json()['name'] == training_history['result'], \
        (
            'resulting state from progress is invalid '
            'or not what we expect'
        )


@skipif(test_create_regimen=fail)
def test_progression(
    mouse,
    mtrain_client, 
    progression,
    regimen,
    training_session_base,
):
    start_state = progression['start']
    end_state = progression['end']
    training_session_base.update(
        progression['overrides']
    )

    mtrain_client.
