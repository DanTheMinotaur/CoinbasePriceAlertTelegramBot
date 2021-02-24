from app.service import BotService, Notifier, State


def test_get_nearest_increments():
    """ Tests rounding increments"""
    tests = [
        (1000, 100, 1000,),
        (6.32, 5, 5,),
        (1.92, 0.10, 1.90,),
        (43577.22, 1000, 43000,),
        (32022.12, 0.50, 32022,),
    ]
    for price, increment, expected in tests:
        result = BotService.get_nearest_increment(price, increment)
        assert result == expected


def test_is_incremented():
    t1 = Notifier(
        currency='EUR',
        increment=500,
        price_type='spot',
        crypto='BTC',
        internals=State(
            last_alert=43500.00,
            last_price=43782.22
        ),
        chat_id=1
    )

    assert BotService.is_incremented(44402.11, t1)
    assert BotService.is_incremented(43000.00, t1)
    assert not BotService.is_incremented(43301.24, t1)
    assert not BotService.is_incremented(43500.24, t1)

    t2 = Notifier(
        currency='USD',
        increment=0.10,
        price_type='spot',
        crypto='BTC',
        internals=State(
            last_alert=19.30,
            last_price=19.22
        ),
        chat_id=1
    )

    assert BotService.is_incremented(19.50, t2)
    assert BotService.is_incremented(18.22, t2)
    assert not BotService.is_incremented(19.27, t2)
    assert not BotService.is_incremented(19.30, t2)
