api_resource_not_found={'status':404,'message':'Resource Not Found'}


class GenerateError:
    def default(self,err_type):
        return err_type