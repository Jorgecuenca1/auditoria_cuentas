from django.shortcuts import render, redirect
from .models import Factura, RipsItem
from .forms import FacturaForm
from accounts.models import Profile
import json


def radicar_factura(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST, request.FILES)
        if form.is_valid():
            factura = form.save(commit=False)
            factura.ips = Profile.objects.get(user=request.user)
            factura.estado_auditoria = "Radicada"
            factura.save()

            archivo = factura.archivo_rips.open()
            data = json.load(archivo)

            for usuario in data.get("usuarios", []):
                pid = usuario.get("numDocumentoIdentificacion")
                servicios = usuario.get("servicios", {})
                for tipo, lista in servicios.items():
                    for item in lista:
                        codigo = (
                            item.get("codConsulta")
                            or item.get("codProcedimiento")
                            or item.get("codTecnologiaSalud")
                            or "SIN_CODIGO"
                        )
                        descripcion = item.get("nomTecnologiaSalud") or "Sin descripción"
                        fecha = (
                            item.get("fechaInicioAtencion")
                            or item.get("fechaDispensAdmon")
                            or item.get("fechaSuministroTecnologia")
                            or ""
                        )
                        diagnostico = item.get("codDiagnosticoPrincipal") or "SIN_DIAG"
                        valor = item.get("vrServicio") or 0
                        cod_prestador = item.get("codPrestador") or ""

                        RipsItem.objects.create(
                            factura=factura,
                            tipo_servicio=tipo,
                            paciente_id=item.get("numDocumentoIdentificacion", pid),
                            codigo=codigo,
                            descripcion=descripcion,
                            fecha=fecha,
                            diagnostico=diagnostico,
                            valor=valor,
                            cod_prestador=cod_prestador
                        )

            return redirect('facturacion:radicar_factura')
    else:
        form = FacturaForm()

    return render(request, 'facturacion/radicar_factura.html', {'form': form})
