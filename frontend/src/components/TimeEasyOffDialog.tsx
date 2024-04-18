import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { useFormik } from "formik";
import { TimeEasyOffFrom } from "./time-easy-off-from";
import { useState } from "react";

export type FormikReturnType = ReturnType<typeof useFormik>;

export function TimeEasyOffDialog(props: { onSuccess: () => void }) {
  const [open, setOpen] = useState(false);

  const handleOpenChange = () => {
    setOpen((prev) => !prev);
  };

  const handleSuccess = () => {
    props.onSuccess();
    handleOpenChange();
  };

  return (
    <Dialog onOpenChange={handleOpenChange} open={open}>
      <DialogTrigger asChild>
        <Button variant="outline">create a leave request</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <TimeEasyOffFrom onSuccess={handleSuccess} />
      </DialogContent>
    </Dialog>
  );
}
