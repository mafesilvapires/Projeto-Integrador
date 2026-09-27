import hashlib
import hmac
import json
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import IntegridadeLog

GENESIS_HASH = '0' * 64

def calculate_hash(data, previous_hash):
    msg = f"{previous_hash} | {data}".encode('utf-8')

    return hmac.new(
            settings.LOG_INTEGRITY_KEY.encode('utf-8'),
            msg,
            hashlib.sha256
            ).hexdigest()

def event_register(event, data):
    canon_data = json.dumps(
            data,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":")
            )

    with transaction.atomic():

        last = (
                IntegridadeLog.objects
                .select_for_update()
                .order_by("-id")
                .first()
                )

        previous_hash = (
                last.actual_hash
                if last
                else GENESIS_HASH
                )

        new_hash = calculate_hash(
                canon_data,
                previous_hash
                )

        register = IntegridadeLog.objects.create(
                timestamp=timezone.now(),
                event=event,
                data=canon_data,
                previous_hash=previous_hash,
                actual_hash=new_hash
                )
    return register
