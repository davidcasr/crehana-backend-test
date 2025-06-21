"""Email service for sending notifications."""

import logging
from datetime import datetime
from typing import Optional
from abc import ABC, abstractmethod

from ...domain.models.entities import User, Task, TaskList


# Configurar logger para las notificaciones
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService(ABC):
    """Abstract base class for email services."""

    @abstractmethod
    def send_task_assignment_email(
        self,
        user: User,
        task: Task,
        task_list: TaskList,
        assigned_by: Optional[User] = None,
    ) -> bool:
        """Send email notification when a task is assigned to a user."""
        pass

    @abstractmethod
    def send_task_completion_email(
        self, user: User, task: Task, task_list: TaskList
    ) -> bool:
        """Send email notification when a task is completed."""
        pass


class MockEmailService(EmailService):
    """Mock email service for development and testing."""

    def __init__(self):
        self.sent_emails = []  # Para testing/debugging

    def send_task_assignment_email(
        self,
        user: User,
        task: Task,
        task_list: TaskList,
        assigned_by: Optional[User] = None,
    ) -> bool:
        """Simulate sending task assignment email."""
        try:
            # Crear el contenido del email
            subject = f"📋 Nueva tarea asignada: {task.title}"

            # Determinar quién asignó la tarea
            assigned_by_text = f" por {assigned_by.full_name}" if assigned_by else ""

            # Crear el cuerpo del email
            email_body = f"""
            ╔══════════════════════════════════════════════════════════════╗
            ║                    🎯 NUEVA TAREA ASIGNADA                   ║
            ╠══════════════════════════════════════════════════════════════╣
            ║                                                              ║
            ║ Hola {user.full_name},                                       ║
            ║                                                              ║
            ║ Se te ha asignado una nueva tarea{assigned_by_text}:         ║
            ║                                                              ║
            ║ 📌 Tarea: {task.title}                                       ║
            ║ 📝 Descripción: {task.description or 'Sin descripción'}     ║
            ║ 📊 Lista: {task_list.name}                                   ║
            ║ ⚡ Prioridad: {task.priority.value.upper()}                  ║
            ║ 📅 Fecha límite: {task.due_date.strftime('%d/%m/%Y %H:%M') if task.due_date else 'No definida'} ║
            ║                                                              ║
            ║ 🔗 Accede al sistema para ver más detalles.                 ║
            ║                                                              ║
            ║ ¡Éxito en tu nueva tarea! 🚀                                ║
            ║                                                              ║
            ╚══════════════════════════════════════════════════════════════╝
            """

            # Simular envío del email
            print("\n" + "=" * 80)
            print("📧 EMAIL ENVIADO (SIMULACIÓN)")
            print("=" * 80)
            print(f"📨 Para: {user.email} ({user.full_name})")
            print(f"📋 Asunto: {subject}")
            print(f"🕐 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print("\n📄 CONTENIDO:")
            print(email_body)
            print("=" * 80)

            # Guardar email para debugging
            email_record = {
                "timestamp": datetime.now(),
                "to": user.email,
                "to_name": user.full_name,
                "subject": subject,
                "type": "task_assignment",
                "task_id": task.id,
                "task_title": task.title,
                "task_list": task_list.name,
                "assigned_by": assigned_by.full_name if assigned_by else None,
                "status": "sent",
            }
            self.sent_emails.append(email_record)

            logger.info(
                f"✅ Email de asignación enviado a {user.email} para tarea '{task.title}'"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error enviando email de asignación: {str(e)}")
            return False

    def send_task_completion_email(
        self, user: User, task: Task, task_list: TaskList
    ) -> bool:
        """Simulate sending task completion email."""
        try:
            subject = f"✅ Tarea completada: {task.title}"

            email_body = f"""
            ╔══════════════════════════════════════════════════════════════╗
            ║                    🎉 TAREA COMPLETADA                       ║
            ╠══════════════════════════════════════════════════════════════╣
            ║                                                              ║
            ║ ¡Felicidades {user.full_name}!                              ║
            ║                                                              ║
            ║ Has completado exitosamente la siguiente tarea:             ║
            ║                                                              ║
            ║ ✅ Tarea: {task.title}                                       ║
            ║ 📝 Descripción: {task.description or 'Sin descripción'}     ║
            ║ 📊 Lista: {task_list.name}                                   ║
            ║ 🏁 Completada el: {datetime.now().strftime('%d/%m/%Y %H:%M')} ║
            ║                                                              ║
            ║ ¡Excelente trabajo! 🎯                                      ║
            ║                                                              ║
            ╚══════════════════════════════════════════════════════════════╝
            """

            print("\n" + "=" * 80)
            print("📧 EMAIL ENVIADO (SIMULACIÓN)")
            print("=" * 80)
            print(f"📨 Para: {user.email} ({user.full_name})")
            print(f"📋 Asunto: {subject}")
            print(f"🕐 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print("\n📄 CONTENIDO:")
            print(email_body)
            print("=" * 80)

            # Guardar email para debugging
            email_record = {
                "timestamp": datetime.now(),
                "to": user.email,
                "to_name": user.full_name,
                "subject": subject,
                "type": "task_completion",
                "task_id": task.id,
                "task_title": task.title,
                "task_list": task_list.name,
                "status": "sent",
            }
            self.sent_emails.append(email_record)

            logger.info(
                f"✅ Email de completación enviado a {user.email} para tarea '{task.title}'"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error enviando email de completación: {str(e)}")
            return False

    def get_sent_emails(self) -> list:
        """Get list of sent emails for debugging/testing."""
        return self.sent_emails

    def clear_sent_emails(self):
        """Clear sent emails list."""
        self.sent_emails.clear()


# Instancia global del servicio de email
email_service = MockEmailService()


def get_email_service() -> EmailService:
    """Get the email service instance."""
    return email_service
