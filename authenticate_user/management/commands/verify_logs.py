import hmac
from datetime import timezone as dt_timezone
from django.utils import timezone
from django.core.management.base import BaseCommand
from authenticate_user.models import IntegridadeLog
from authenticate_user.log_integrity import calculate_hash, GENESIS_HASH


class Command(BaseCommand):

    help = 'Verifica a integridade da cadeia de logs.'

    def handle(self, *args, **options):

        registros = IntegridadeLog.objects.order_by('id')

        if not registros.exists():
            self.stdout.write(
                self.style.WARNING(
                    'Nenhum Registro de Log Encontrado.'
                )
            )
            return

        previous_hash = GENESIS_HASH
        qtd = 0

        for registro in registros:

            if registro.previous_hash != previous_hash:
                self.stderr.write(
                    self.style.ERROR(
                        f'[ERRO] Cadeia quebrada no registro '
                        f'{registro.id} ({registro.event}).'
                    )
                )

                self.stderr.write(
                    f'Hash anterior esperado: {previous_hash}'
                )

                self.stderr.write(
                    f'Hash encontrado: {registro.previous_hash}'
                )

                return

            ts = registro.timestamp
            if timezone.is_naive(ts):
                ts = timezone.make_aware(ts, dt_timezone.utc)

            calculated_hash = calculate_hash(
                ts,
                registro.event,
                registro.data,
                registro.previous_hash
            )

            if not hmac.compare_digest(
                registro.actual_hash,
                calculated_hash
            ):
                self.stderr.write(
                    self.style.ERROR(
                        f'[ERRO] Integridade comprometida no '
                        f'registro {registro.id} ({registro.event}).'
                    )
                )

                self.stderr.write(
                    f'Hash armazenado: {registro.actual_hash}'
                )

                self.stderr.write(
                    f'Hash recalculado: {calculated_hash}'
                )

                return

            previous_hash = registro.actual_hash
            qtd += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'[OK] Integridade Validada: '
                f'{qtd} registros verificados.'
            )
        )
